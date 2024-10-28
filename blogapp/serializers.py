from rest_framework import serializers
from .models import Posts, UserData
from django.core.validators import validate_email
from django.forms import ValidationError
from django.contrib.auth.hashers import make_password, check_password



class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = ['username', 'email','password']
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
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError("Must include both username and password.")

        try:
            user = UserData.objects.get(username=username)
        except UserData.DoesNotExist:
            raise serializers.ValidationError("User with this username does not exist.")
        
        
        data['user'] = user
        return data

class OTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    
    
    
    
class PostViewSerializer(serializers.ModelSerializer):
    model = Posts
    fields = ["id", "title", ]
    
    class Meta:
        model = Posts
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at']
        
