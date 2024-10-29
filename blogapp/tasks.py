from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_welcome_email(user_email):
    print(f"::::::::: {user_email} :::::::::::")   
    res = send_mail(
        'Welcome!',
        'Thank you for signing up!',
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )
    print(f"::::::::: {res} :::::::::::")   