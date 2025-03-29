##############################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2025, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##############################################################################

"""SMS Authentication Module for pgAdmin."""

from flask import Flask

from .sms import SMSAuthentication

def init_app(app: Flask):
    """
    Initialize the SMS authentication module.

    Args:
        app (Flask): Flask application object
    """
    # Register the SMS authentication method with the registry
    from pgadmin.authenticate.mfa.registry import MultiFactorAuthRegistry
    from .sms import SMS_AUTH_METHOD
    
    # Register the class with the registry using the correct key
    MultiFactorAuthRegistry._registry[SMS_AUTH_METHOD] = SMSAuthentication
    
    # Log the current state of MFA methods
    import config
    app.logger.info(f"Current MFA_SUPPORTED_METHODS: {config.MFA_SUPPORTED_METHODS}")
    app.logger.info(f"Current MFA registry: {list(MultiFactorAuthRegistry._registry.keys())}")
    
    # Ensure SMS is in supported methods
    if SMS_AUTH_METHOD not in config.MFA_SUPPORTED_METHODS:
        config.MFA_SUPPORTED_METHODS.append(SMS_AUTH_METHOD)
        app.logger.info("Added SMS to MFA_SUPPORTED_METHODS")
    
    # Ensure MFA is enabled
    if not hasattr(config, 'MFA_ENABLED') or not config.MFA_ENABLED:
        config.MFA_ENABLED = True
        app.logger.info("Enabled MFA")

__all__ = ['SMSAuthentication', 'init_app'] 