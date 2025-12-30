import random
import string
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)

def generate_otp(length=None):
    """
    Generate a random OTP of specified length.
    Default length is taken from settings.OTP_LENGTH
    """
    if length is None:
        length = getattr(settings, 'OTP_LENGTH', 6)
    
    return ''.join(random.choices(string.digits, k=length))

def send_otp_sms(phone_number, otp):
    """
    Send OTP via SMS using Twilio.
    Returns True if successful, False otherwise.
    """
    try:
        # Check if Twilio credentials are configured
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        twilio_phone = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
        
        if not all([account_sid, auth_token, twilio_phone]):
            logger.warning("Twilio credentials not configured. OTP not sent.")
            # For development, we'll simulate sending SMS
            if settings.DEBUG:
                logger.info(f"DEBUG MODE: OTP for {phone_number} is: {otp}")
                return True
            return False
        
        # Skip actual SMS sending if using placeholder credentials
        if account_sid == 'your_twilio_account_sid_here':
            logger.info(f"DEBUG MODE: OTP for {phone_number} is: {otp}")
            return True
            
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send SMS
        message = client.messages.create(
            body=f"Your Pet Rescue verification code is: {otp}. This code expires in {settings.OTP_EXPIRY_MINUTES} minutes.",
            from_=twilio_phone,
            to=phone_number
        )
        
        logger.info(f"OTP sent successfully to {phone_number}. Message SID: {message.sid}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send OTP to {phone_number}: {str(e)}")
        # In debug mode, still show the OTP in console
        if settings.DEBUG:
            logger.info(f"DEBUG MODE: OTP for {phone_number} is: {otp}")
            return True
        return False

def store_otp_in_session(request, phone_number, otp):
    """
    Store OTP and related data in session for verification.
    """
    expiry_time = timezone.now() + timedelta(minutes=getattr(settings, 'OTP_EXPIRY_MINUTES', 5))
    
    request.session['otp_data'] = {
        'otp': otp,
        'phone_number': phone_number,
        'expiry': expiry_time.isoformat(),
        'attempts': 0
    }
    request.session.modified = True

def verify_otp_from_session(request, entered_otp, phone_number):
    """
    Verify OTP from session data.
    Returns tuple (is_valid, error_message)
    """
    otp_data = request.session.get('otp_data')
    
    if not otp_data:
        return False, "No OTP found. Please request a new one."
    
    # Check if phone number matches
    if otp_data.get('phone_number') != phone_number:
        return False, "Phone number mismatch."
    
    # Check expiry
    expiry_time = datetime.fromisoformat(otp_data['expiry'])
    if timezone.now() > expiry_time:
        # Clear expired OTP
        if 'otp_data' in request.session:
            del request.session['otp_data']
        return False, "OTP has expired. Please request a new one."
    
    # Check attempts (max 3 attempts)
    if otp_data.get('attempts', 0) >= 3:
        # Clear OTP after max attempts
        if 'otp_data' in request.session:
            del request.session['otp_data']
        return False, "Maximum attempts exceeded. Please request a new OTP."
    
    # Verify OTP
    if otp_data.get('otp') == entered_otp:
        # Clear OTP after successful verification
        if 'otp_data' in request.session:
            del request.session['otp_data']
        return True, "OTP verified successfully."
    else:
        # Increment attempts
        otp_data['attempts'] = otp_data.get('attempts', 0) + 1
        request.session['otp_data'] = otp_data
        request.session.modified = True
        
        remaining_attempts = 3 - otp_data['attempts']
        if remaining_attempts > 0:
            return False, f"Invalid OTP. {remaining_attempts} attempts remaining."
        else:
            # Clear OTP after max attempts
            if 'otp_data' in request.session:
                del request.session['otp_data']
            return False, "Invalid OTP. Maximum attempts exceeded."

def clear_otp_session(request):
    """
    Clear OTP data from session.
    """
    if 'otp_data' in request.session:
        del request.session['otp_data']
        request.session.modified = True

def format_phone_number(phone_number):
    """
    Format phone number for consistency.
    Adds +1 if no country code is present and removes any non-digit characters except +.
    """
    # Remove all non-digit characters except +
    cleaned = ''.join(char for char in phone_number if char.isdigit() or char == '+')
    
    # If no + at the beginning, add +1 (US country code)
    if not cleaned.startswith('+'):
        if len(cleaned) == 10:  # US phone number without country code
            cleaned = '+1' + cleaned
        elif len(cleaned) == 11 and cleaned.startswith('1'):  # US phone number with 1 prefix
            cleaned = '+' + cleaned
        else:
            cleaned = '+1' + cleaned  # Default to US
    
    return cleaned