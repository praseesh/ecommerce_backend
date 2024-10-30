from rest_framework import serializers
from .models import Posts, UserData
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
            raise serializers.ValidationError("Must include both username and password.")
        try:
            user = UserData.objects.get(email=email)
        except UserData.DoesNotExist:
            raise serializers.ValidationError("User with this Email does not exist.")
        if not check_password(password, user.password):
            print(f":::::    {password}:::::::   {user.password}")
            raise serializers.ValidationError("Incorrect password.")
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
    
class PostViewSerializer(serializers.ModelSerializer):
    model = Posts
    fields = ["id", "title", ]
    
    class Meta:
        model = Posts
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at']
        
