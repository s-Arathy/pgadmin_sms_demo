import sys
import os

# Add the web directory to the Python path
web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, web_dir)

from twilio.rest import Client
import config
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_twilio_connection():
    """Test Twilio connection and credentials"""
    try:
        # Log config values (masked for security)
        logger.info(f"Using Account SID: {config.TWILIO_ACCOUNT_SID[:6]}...{config.TWILIO_ACCOUNT_SID[-4:]}")
        logger.info(f"Using Phone Number: {config.TWILIO_PHONE_NUMBER}")
        
        client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
        account = client.api.accounts(config.TWILIO_ACCOUNT_SID).fetch()
        logger.info(f"Successfully connected to Twilio account: {account.friendly_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Twilio: {str(e)}")
        return False

def test_send_sms(phone_number):
    """Test sending SMS using Twilio"""
    try:
        client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
        test_code = "123456"  # Test OTP
        
        logger.info(f"Attempting to send SMS to {phone_number}")
        message = client.messages.create(
            body=f"Your pgAdmin test verification code is: {test_code}",
            from_=config.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        logger.info(f"Successfully sent SMS. Message SID: {message.sid}")
        return True, message.sid
    except Exception as e:
        logger.error(f"Failed to send SMS: {str(e)}")
        return False, str(e)

if __name__ == "__main__":
    # Test phone number
    test_phone = "+919567283578"  # Your phone number
    
    logger.info("Testing Twilio connection...")
    if test_twilio_connection():
        logger.info("Twilio connection successful!")
        
        logger.info(f"Testing SMS sending to {test_phone}...")
        success, result = test_send_sms(test_phone)
        if success:
            logger.info("SMS sent successfully!")
        else:
            logger.error(f"Failed to send SMS: {result}")
    else:
        logger.error("Failed to connect to Twilio") 