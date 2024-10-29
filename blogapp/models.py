from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, validate_email

phone_regex = RegexValidator(
    regex=r"^\d{10}", message="Phone number must be 10 digits only."
)
class UserData(models.Model):
    username = models.CharField(max_length=100,null=False,blank=False)
    email = models.EmailField(max_length=100, null=False,blank=False,unique=True)
    phone = models.CharField(max_length=10, blank=False,null=False, unique=True, validators=[phone_regex])
    password = models.CharField(max_length=128,null=False,blank=False)
    
    def __str__(self):
        return self.username
    class Meta:
        db_table = 'userdata'
        
class TemporaryUserRegistration(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=128)  
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'tempuser'
    
    
class OTPVerification(models.Model):
    user = models.OneToOneField(UserData, on_delete=models.CASCADE, null=True, blank=True)
    otp = models.CharField(max_length=6)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return (timezone.now() - self.created_at).total_seconds() > 300 
    class Meta:
        db_table = 'otp'
        ordering = ['-created_at']
        
class Posts(models.Model):
    title = models.CharField(max_length=40,null=False,blank=False)
    content = models.TextField(max_length=1000, null=False,blank=False)
    author = models.ForeignKey(UserData, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']

    def __str__(self):
        return self.title