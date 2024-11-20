from rest_framework import serializers
from .models import UserData
from django.core.validators import validate_email
from django.forms import ValidationError
from django.contrib.auth.hashers import make_password, check_password



class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = ['username', 'email', 'phone','password']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    def validate_username(self, value):
        if len(value) < 4:
            raise serializers.ValidationError("Username must be at least 4 characters long.")
        return value
    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        return value
    
    def validate_password(self, value):
        if len(value) < 4:
            raise serializers.ValidationError("Password must be at least 4 characters long.")
        return value
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
        
class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Must include both email and password.")

        try:
            user = UserData.objects.get(email=email)
        except UserData.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        if not check_password(password, user.password):
            raise serializers.ValidationError("Incorrect password.")

        if not user.is_active:
            raise serializers.ValidationError("The requested email is temporarily blocked. Please contact the admin.")

        data['user'] = user
        return data

class OTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=10, required=False)

    def validate(self, data):
        if not data.get('email') and not data.get('phone'):
            raise serializers.ValidationError("Either email or phone number must be provided.")
        return data


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=10, required=False)
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        if not data.get('email') and not data.get('phone'):
            raise serializers.ValidationError("Either email or phone number must be provided.")
        return data  
    
        
class UserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = '__all__'
        
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = ['firstname', 'lastname', 'username', 'phone', 'email', 'gender', 'age', 'city', 'profile_photo' ]
    
    def validate_firstname(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("First name should contain only alphabetic characters.")
        return value.capitalize()  

    def validate_lastname(self, value):
        if value:
            if not value.isalpha():
                raise serializers.ValidationError("Last name should contain only alphabetic characters.")
            return value.capitalize()  
        return value
    
    def validate_age(self, value):
        if value is not None and (value < 18 or value > 100):
            raise serializers.ValidationError("Age must be between 18 and 100.")
        return value
    
    def validate(self,data):
        if not data.get('firstname') or not data.get('lastname'):
            raise serializers.ValidationError('Both Firstname and Lastname Required')
        gender = data.get('gender')
        if gender and gender not in ['Male', 'Female', 'Other']:
            raise serializers.ValidationError('Gender Must be Male or Female or Other')
        return data
