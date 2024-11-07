from django.core.mail import EmailMessage
from django.conf import settings

def send_mail_otp(email, welcome_message):
    try:
        subject = "Welcome Message"
        sender_name = "Praseesh P"
        sender_email = settings.EMAIL_HOST_USER
        recipient_email = email

        message_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #0066cc;">Welcome Message</h2>
                <p>Hello,</p>
                <p style="font-size: 30px; font-weight: bold; color: #0066cc;">{welcome_message}</p>
                <p><strong>This is Your Welcome Message</strong>.</p>
                <p>If you did not request this, please ignore this email.</p>
                <hr>
                <footer style="font-size: 12px; color: #888;">
                    <p>Thank you,<br>{'Praseesh P'}</p>
                </footer>
            </body>
        </html>
        """

        email_message = EmailMessage(
            subject=subject,
            body=message_content,
            from_email=f"{sender_name} <{sender_email}>",
            to=[recipient_email],
        )
        email_message.content_subtype = "html"  
        email_message.send(fail_silently=False)
        return welcome_message
    except Exception as e:
        print(f"Error sending OTP via email: {e}")
        return None
