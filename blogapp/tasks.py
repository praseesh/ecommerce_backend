from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from .utils import send_mail_otp, send_otp  
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_mail_otp_task(email, otp):
    return send_mail_otp(email, otp)  

@shared_task
def send_sms_otp_task(mobile, otp):
    return send_otp(mobile, otp)  
 