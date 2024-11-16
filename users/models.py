from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, validate_email
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin

phone_regex = RegexValidator(
    regex=r"^\d{10}", message="Phone number must be 10 digits only."
)

class UserDataManager(BaseUserManager):
    def create_user(self, email, username, phone, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email), username=username, phone=phone)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, phone, password=None):
        user = self.create_user(email, username, phone, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class UserData(AbstractBaseUser,PermissionsMixin):
    firstname = models.CharField(max_length=30, null=True, blank=True)
    lastname = models.CharField(max_length=30, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='images/',blank=True,null=True)
    age = models.IntegerField(null=True,blank=True)
    gender = models.CharField(max_length=10,blank=True,null=True)
    city = models.CharField(max_length=255,blank=True,null=True)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=10, unique=True, validators=[phone_regex])
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'   
    REQUIRED_FIELDS = ['username', 'phone']   

    objects = UserDataManager()  

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
        return (timezone.now() - self.created_at).total_seconds() > 3600 
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

class Address(models.Model):
    user = models.ForeignKey(UserData,on_delete=models.CASCADE)
    house =models.CharField(max_length=255)
    area =models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    pin_code = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'address'
        ordering = ['-created_at']

    def __str__(self):
        return self.user