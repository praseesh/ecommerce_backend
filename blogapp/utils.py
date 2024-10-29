import random
import requests
from django.conf import settings
from django.core.mail import send_mail

def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))

def send_otp(mobile, otp):
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

# def send_mail_otp(email, otp):
#     """Send the generated OTP via email to the given email address."""
#     try:
#         print(f"++++:::::::{email,otp}::::::::::++++")
        
#         send_mail(
#             'Your OTP Verification Code',
#             f'Your OTP code is {otp}. It is valid for 5 minutes.',
#             'prasee5264@gmail.com',  
#             [email],
#             fail_silently=False,
#         )
#         print(f"****:::::::{email,otp}::::::::::****")
        
#         return otp
#     except Exception as e:
#         print(f"Error sending OTP via email: {e}")
#         return None

from django.core.mail import send_mail, EmailMessage
from email.mime.text import MIMEText
from django.conf import settings

def send_mail_otp(email, otp):
    try:
        message_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #0066cc;">Your One-Time Password (OTP)</h2>
                <p>Hello,</p>
                <p>Your OTP for secure access is:</p>
                <p style="font-size: 24px; font-weight: bold; color: #0066cc;">{otp}</p>
                <p>This code is valid for <strong>5 minutes</strong>.</p>
                <p>If you did not request this, please ignore this email.</p>
                <hr>
                <footer style="font-size: 12px; color: #888;">
                    <p>Thank you,<br>{'Praseesh P'}</p>
                </footer>
            </body>
        </html>
        """
        message = MIMEText(message_content, "html")

        subject = "Your Secure Access OTP Code"
        sender_name = "Praseesh P"
        sender_email = settings.EMAIL_HOST_USER
        recipient_email = email
        email_message = EmailMessage(
            subject=subject,
            body=message_content,
            from_email=f"{sender_name} <{sender_email}>",
            to=[recipient_email],
        )
        email_message.content_subtype = "html"  

        email_message.send(fail_silently=False)
        return otp

    except Exception as e:
        print(f"Error sending OTP via email: {e}")
        return None