##############################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2025, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##############################################################################
"""Multi-factor Authentication implementation by sending OTP through SMS"""

from flask import url_for, session, Response, render_template, current_app, \
    flash, Blueprint, request
from flask_babel import gettext as _
from flask_login import current_user

import config
from pgadmin.utils.csrf import pgCSRFProtect
from pgadmin.authenticate.mfa.registry import BaseMFAuth
from pgadmin.authenticate.mfa.utils import ValidationException, mfa_add, fetch_auth_option
from pgadmin.utils.constants import MessageType

def __generate_otp() -> str:
    """
    Generate a six-digits one-time-password (OTP) for the current user.

    Returns:
        str: A six-digits OTP for the current user
    """
    import time
    import codecs
    import secrets

    code = codecs.encode("{}{}{}".format(
        time.time(), current_user.username, secrets.choice(range(1000, 9999))
    ).encode(), "hex")

    res = 0
    idx = 0

    while idx < len(code):
        res += int((code[idx:idx + 6]).decode('utf-8'), base=16)
        res %= 1000000
        idx += 5

    return str(res).zfill(6)

def _send_code_to_phone(_phone: str = None) -> (bool, int, str):
    """
    Send the code to the phone number via SMS.

    Args:
        _phone (str, optional): Phone number where to send the OTP code.
                               Defaults to None.

    Returns:
        (bool, int, str): Returns a set as (failed?, HTTP Code, message string)
    """
    if not current_user.is_authenticated:
        current_app.logger.error("User not authenticated when trying to send SMS")
        return False, 401, _("Not accessible")

    if _phone is None:
        _phone = session.get('mfa_phone_number', None)

    if _phone is None:
        current_app.logger.error("No phone number provided or found in session")
        return False, 401, _("No phone number is available.")

    try:
        session["mfa_sms_code"] = __generate_otp()
        current_app.logger.info(f"Generated OTP code for phone {_phone}")
        
        # Validate Twilio configuration
        if not hasattr(config, 'TWILIO_ACCOUNT_SID') or not config.TWILIO_ACCOUNT_SID:
            current_app.logger.error("Twilio Account SID not configured")
            return False, 503, _("Twilio Account SID not configured")
            
        if not hasattr(config, 'TWILIO_AUTH_TOKEN') or not config.TWILIO_AUTH_TOKEN:
            current_app.logger.error("Twilio Auth Token not configured")
            return False, 503, _("Twilio Auth Token not configured")
            
        if not hasattr(config, 'TWILIO_PHONE_NUMBER') or not config.TWILIO_PHONE_NUMBER:
            current_app.logger.error("Twilio Phone Number not configured")
            return False, 503, _("Twilio Phone Number not configured")
        
        # Send SMS using Twilio
        from twilio.rest import Client
        current_app.logger.info("Initializing Twilio client")
        client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
        
        current_app.logger.info(f"Sending SMS from {config.TWILIO_PHONE_NUMBER} to {_phone}")
        
        message = client.messages.create(
            body=f"Your pgAdmin verification code is: {session['mfa_sms_code']}",
            from_=config.TWILIO_PHONE_NUMBER,
            to=_phone
        )
        
        current_app.logger.info(f"SMS sent successfully. Message SID: {message.sid}")
        
        # For development, also log the code
        current_app.logger.info(
            f"SMS Code for {_phone}: {session['mfa_sms_code']}"
        )
        
    except ImportError as e:
        current_app.logger.exception("Failed to import Twilio client")
        return False, 503, _("Twilio client not installed. Please install 'twilio' package.")
    except Exception as e:
        current_app.logger.exception(f"Failed to send SMS: {str(e)}")
        error_message = str(e)
        if "not a valid phone number" in error_message.lower():
            return False, 400, _("Invalid phone number format")
        elif "authenticate" in error_message.lower():
            return False, 503, _("Invalid Twilio credentials")
        else:
            return False, 503, _("Failed to send the code via SMS.") + "\n" + error_message

    message = _(
        "A verification code was sent to {}. Check your phone and enter "
        "the code."
    ).format(_mask_phone(_phone))

    return True, 200, message

def _mask_phone(_phone: str) -> str:
    """
    Mask the phone number for display.

    Args:
        _phone (str): Phone number to be masked

    Returns:
        str: Masked phone number
    """
    return '*' * (len(_phone) - 4) + _phone[-4:]

def send_sms_code() -> Response:
    """
    Send the code to the user's phone number.

    Returns:
        Flask.Response: Response containing the HTML portion after sending the
                       code to the registered phone number of the user.
    """
    if not current_user.is_authenticated:
        current_app.logger.error("User not authenticated when trying to send SMS code")
        return Response(_("Not accessible"), 401, mimetype='text/html')

    phone = request.form.get('send_to')
    current_app.logger.info(f"Attempting to send SMS code to phone number: {phone}")
    
    if not phone:
        current_app.logger.error("No phone number provided in request")
        return Response(_("No phone number provided"), 400, mimetype='text/html')
        
    # Validate phone number format
    import re
    if not re.match(r'^\+[1-9]\d{1,14}$', phone):
        current_app.logger.error(f"Invalid phone number format: {phone}")
        return Response(_("Invalid phone number format. Please use format: +919567283578"), 400, mimetype='text/html')

    success, http_code, message = _send_code_to_phone(phone)
    
    if success:
        current_app.logger.info(f"Successfully sent SMS code to {phone}")
        session['mfa_phone_number'] = phone
        # Return a response that will trigger the verification view
        return Response(render_template(
            "mfa/register.html", _=_,
            mfa_list=list(),
            mfa_view=dict(
                label=_('SMS Authentication'),
                auth_method='sms',
                description=_('Enter the verification code sent to your phone'),
                otp_placeholder=_('Enter 6-digit code'),
                show_verification=True
            ),
            next_url=request.form.get('next', 'internal'),
            error_message=None
        ), 200, mimetype='text/html')
    else:
        current_app.logger.error(f"Failed to send SMS code to {phone}. HTTP Code: {http_code}, Message: {message}")
        return Response(message, http_code, mimetype='text/html')

@pgCSRFProtect.exempt
def javascript() -> Response:
    """
    Returns the javascript code for the SMS authentication method.

    Returns:
        Flask.Response: Response object containing the javascript code for the
                       SMS auth method.
    """
    if not current_user.is_authenticated:
        return Response(_("Not accessible"), 401, mimetype="text/plain")

    return Response(render_template(
        "mfa/sms.js", _=_, url_for=url_for,
    ), 200, mimetype="text/javascript")

SMS_AUTH_METHOD = 'sms'

def sms_authentication_label():
    return _('SMS Authentication')

class SMSAuthentication(BaseMFAuth):
    @property
    def name(self):
        return SMS_AUTH_METHOD

    @property
    def label(self):
        return sms_authentication_label()

    @property
    def icon(self):
        return url_for("mfa.static", filename="images/sms_lock.svg")

    @property
    def validate_script(self):
        return url_for('mfa.javascript_sms')

    def validate(self, **kwargs):
        code = kwargs.get('code', None)
        sms_otp = session.get("mfa_sms_code", None)
        if code is not None and sms_otp is not None and code == sms_otp:
            session.pop("mfa_sms_code")
            return
        raise ValidationException("Invalid code")

    def validation_view(self):
        session.pop("mfa_sms_code", None)
        return dict(
            description=_("Verify with SMS Authentication"),
            button_label=_("Send Code"),
            button_label_sending=_("Sending Code...")
        )

    def registration_view(self, form_data):
        """
        Handle SMS registration view.

        Args:
            form_data (dict): Form data from the request

        Returns:
            dict: View data for React component rendering
        """
        current_app.logger.debug(f"SMS registration_view called with form_data: {form_data}")
        
        # Initial setup view
        if form_data.get('sms') == 'SETUP' or form_data.get(self.name) == 'SETUP':
            current_app.logger.debug("SMS setup view requested")
            # Clear any existing session data
            session.pop('mfa_sms_code', None)
            session.pop('mfa_phone_number', None)
            
            return dict(
                label=sms_authentication_label(),
                auth_method=SMS_AUTH_METHOD,
                description=_('Enter your phone number to receive verification codes'),
                phone_number_placeholder=_('Phone number with country code'),
                note=_('Enter your phone number with country code (e.g., +1234567890)')
            )
        
        validate_action = form_data.get('validate')
        current_app.logger.debug(f"Validate action: {validate_action}")
        
        # If sending code
        if validate_action == 'send_code':
            current_app.logger.debug("Processing send_code action")
            phone = form_data.get('send_to')
            if not phone:
                flash(_('Please enter a phone number'), MessageType.ERROR)
                return self.registration_view({'sms': 'SETUP'})  # Return to setup view
                
            # Validate phone number format
            import re
            if not re.match(r'^\+[1-9]\d{1,14}$', phone):
                flash(_('Invalid phone number format. Please use format: +919567283578'), MessageType.ERROR)
                return self.registration_view({'sms': 'SETUP'})  # Return to setup view
                
            success, http_code, message = _send_code_to_phone(phone)
            if not success:
                flash(message, MessageType.ERROR)
                return self.registration_view({'sms': 'SETUP'})  # Return to setup view
                
            session['mfa_phone_number'] = phone
            current_app.logger.debug(f"SMS code sent successfully to {phone}")
            
            return dict(
                label=sms_authentication_label(),
                auth_method=SMS_AUTH_METHOD,
                message=message,
                otp_placeholder=_('Enter 6-digit code')
            )
        
        # If verifying code
        if validate_action == 'verify_code':
            current_app.logger.debug("Processing verify_code action")
            code = form_data.get('code')
            if not code:
                flash(_('Please enter the verification code'), MessageType.ERROR)
                return None
                
            stored_phone = session.get('mfa_phone_number')
            if not stored_phone:
                flash(_('Phone number not found. Please start over.'), MessageType.ERROR)
                return self.registration_view({'sms': 'SETUP'})  # Return to setup view
                
            try:
                self.validate(code=code)
                mfa_add(self.name, stored_phone)
                flash(_('SMS authentication registered successfully'), MessageType.SUCCESS)
                # Clear session data after successful registration
                session.pop('mfa_phone_number', None)
                session.pop('mfa_sms_code', None)
                current_app.logger.info(f"SMS authentication registered successfully for phone: {stored_phone}")
                return None
            except ValidationException as e:
                flash(str(e), MessageType.ERROR)
                current_app.logger.error(f"SMS code validation failed: {str(e)}")
                return None
                
        current_app.logger.warning(f"Unhandled validate action: {validate_action}")
        return self.registration_view({'sms': 'SETUP'})  # Return to setup view as fallback

    def to_dict(self):
        """
        Returns a dictionary representation of the SMS authentication method.
        
        Returns:
            dict: Dictionary containing the SMS authentication details
        """
        return {
            "id": self.name,
            "name": self.name,
            "label": self.label,
            "icon": self.icon,
            "auth_method": "sms"
        }

    def register_url_endpoints(self, blueprint: Blueprint):
        """
        Register URL endpoints for SMS authentication.

        Args:
            blueprint (Blueprint): Flask blueprint to register endpoints on
        """
        blueprint.add_url_rule(
            '/send_sms_code',
            'send_sms_code',
            send_sms_code,
            methods=['POST']
        )

        blueprint.add_url_rule(
            '/store_phone',
            'store_phone',
            store_phone,
            methods=['POST']
        )

        blueprint.add_url_rule(
            '/verify_sms_code',
            'verify_sms_code',
            verify_sms_code,
            methods=['POST']
        )

        blueprint.add_url_rule(
            '/sms.js',
            'javascript_sms',
            javascript,
            methods=['GET']
        )

def store_phone() -> Response:
    """Store the phone number in the session."""
    if not current_user.is_authenticated:
        return Response(_("Not accessible"), 401, mimetype='text/html')

    phone = request.form.get('phone')
    if phone:
        session['mfa_phone_number'] = phone
        return Response('OK', 200)
    return Response(_("No phone number provided"), 400)

def verify_sms_code() -> Response:
    """
    Verify the SMS code entered by the user.

    Returns:
        Flask.Response: Response indicating success or failure of verification
    """
    if not current_user.is_authenticated:
        return Response(_("Not accessible"), 401, mimetype='text/html')

    code = request.form.get('code')
    if not code:
        return Response(_("No verification code provided"), 400, mimetype='text/html')

    stored_code = session.get('mfa_sms_code')
    if not stored_code:
        return Response(_("No verification code found. Please request a new code."), 400, mimetype='text/html')

    if code != stored_code:
        return Response(_("Invalid verification code"), 400, mimetype='text/html')

    # Clear the stored code after successful verification
    session.pop('mfa_sms_code', None)
    
    return Response(_("Code verified successfully"), 200, mimetype='text/html') 