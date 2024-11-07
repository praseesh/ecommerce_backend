from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from .models import Posts, UserData

class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = UserData.objects.get(email=email)
        except UserData.DoesNotExist:
            raise ValidationError('Invalid email or password.')

        if not user.check_password(password):
            raise ValidationError('Invalid email or password.')

        if not user.is_superuser:
            raise ValidationError('You are not authorized to access this admin area.')

        attrs['user'] = user
        return attrs
