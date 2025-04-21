import os
import random
import logging
from app import redis_client

def send_otp(phone_number):
    """
    Generate and store OTP for the provided phone number
    """
    try:
        otp = str(random.randint(100000, 999999))
        # Store OTP in Redis with a 5-minute expiration
        redis_client.setex(f'otp:{phone_number}', 300, otp)
        logging.info(f"OTP {otp} stored for phone number {phone_number}")
        return {'success': True, 'message': f'OTP sent successfully: {otp}'}
    except Exception as e:
        logging.error(f"Error storing OTP: {str(e)}")
        return {'success': False, 'error': str(e)}

def verify_otp(phone_number, otp):
    """
    Verify OTP provided by the user
    """
    try:
        # Get stored OTP from Redis
        stored_otp = redis_client.get(f'otp:{phone_number}')
        logging.info(f"Retrieved OTP for {phone_number}: {stored_otp}")
        
        if stored_otp and stored_otp == otp:
            # Delete the OTP after successful verification
            redis_client.delete(f'otp:{phone_number}')
            logging.info(f"OTP verified successfully for {phone_number}")
            return {'success': True}
        
        logging.warning(f"Invalid OTP for {phone_number}")
        return {'success': False, 'error': 'Invalid OTP'}
    except Exception as e:
        logging.error(f"Error verifying OTP: {str(e)}")
        return {'success': False, 'error': str(e)} 