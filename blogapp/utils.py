import requests
from django.conf import settings

def send_otp(mobile,otp):
    try:
        url = f"https://2factor.in/API/V1/{settings.SMS_API_KEY}/SMS/{mobile}/{otp}/Your OTP is"
        response = requests.get('url')
        return otp
    except Exception as e:
        return None
    
    return bool(response.ok)