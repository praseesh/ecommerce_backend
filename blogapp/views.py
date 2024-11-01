from django.core.mail import send_mail
from .models import OTPVerification, Posts
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import OTPVerification, UserData,TemporaryUserRegistration
from .serializers import OTPRequestSerializer, OTPVerifySerializer,UserDataSerializer, PostViewSerializer, UserLoginSerializer, UserProfileSerializer, UserViewSerializer
from .utils import generate_otp, send_mail_otp
from .tasks import send_mail_otp_task, send_sms_otp_task
from django.contrib.auth.hashers import make_password

class UserRegistrationViews(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserDataSerializer(data=request.data)
        if serializer.is_valid():
            otp = generate_otp()
            TemporaryUserRegistration.objects.update_or_create(
                email=request.data['email'],
                defaults={
                    'username': request.data['username'],
                    'phone': request.data['phone'],
                    'password': request.data['password'],
                    'otp': otp,
                })
            email = request.data.get('email')
            phone = request.data.get('phone')
            OTPVerification.objects.update_or_create(email=email, defaults={'otp': otp, 'phone_number': phone})
            if email:
                send_mail_otp_task.delay(email, otp)
            # if phone:
            #     send_sms_otp_task.delay(phone, otp)
            return Response(
                {'message': 'User registration initiated. An OTP has been sent to your email and phone for verification.'},
                status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class VerifyOTPView(APIView): 
    def post(self, request, *args, **kwargs):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_input = serializer.validated_data['otp']
            temp_user = TemporaryUserRegistration.objects.filter(email=email, otp=otp_input).first()
            if temp_user:
                user_data = {
                    'username': temp_user.username,
                    'email': temp_user.email,
                    'phone': temp_user.phone,
                    'password': temp_user.password,}
                
                user_serializer = UserDataSerializer(data=user_data)
                if user_serializer.is_valid():
                    user = user_serializer.save()
                    temp_user.delete() 
                    return Response({'message': 'OTP verified and user created successfully'}, status=status.HTTP_200_OK)
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)  
            return Response({'message':'Login Successfully',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisteredUserListView(APIView):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        users = UserData.objects.all()
        serializer = UserViewSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class EditProfileView(APIView):
    # authentication_classes = [JWTAuthentication]  
    # permission_classes = [IsAuthenticated]
    pass

class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAuthenticated]

    def patch(self,request,*args, **kwargs):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)