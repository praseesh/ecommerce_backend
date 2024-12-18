from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from users.models import UserData

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
class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = ['id', 'firstname', 'lastname', 'username', 'email', 'phone', 'profile_photo', 'age', 'gender', 'city', 'is_active']

class AdminUserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        exclude = ['password']