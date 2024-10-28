import random
import requests
from django.conf import settings

def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))

def send_otp(mobile, otp):
    """Send the generated OTP via SMS to the given mobile number using the 2Factor API."""
    try:
        url = f"https://2factor.in/API/V1/{settings.SMS_API_KEY}/SMS/{mobile}/{otp}/Your OTP is"
        response = requests.get(url)
        if response.ok:
            return otp
        else:
            return None
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return None
