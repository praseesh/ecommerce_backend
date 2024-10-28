from django.core.mail import send_mail
from .models import OTPVerification, Posts
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import OTPVerification, UserData
from .serializers import OTPRequestSerializer, OTPVerifySerializer,UserDataSerializer, PostViewSerializer
from .utils import send_otp,generate_otp,send_mail_otp

class UserRegistrationViews(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserDataSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            otp = generate_otp()
            email = request.data.get('email')
            phone = request.data.get('phone')
            OTPVerification.objects.update_or_create(user=user, defaults={
                'otp': otp, 'email': email, 'phone_number': phone})
            if email:
                send_mail_otp(email, otp)
            if phone:
                send_otp(phone, otp)
            return Response(
                {'message': 'User registration successful.\
                An OTP has been sent to your email \
                and mobile number for verification.'},
                status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class VerifyOTPView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_input = serializer.validated_data['otp']
            user = UserData.objects.filter(email=email).first()
            if user:
                otp_verification = OTPVerification.objects.filter(user=user).first()
                
                if otp_verification and otp_verification.otp == otp_input:
                    if not otp_verification.is_expired():
                        user.is_active = True
                        user.save()
                        return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)
                    return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        
        else:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
class PostView(APIView):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        posts = Posts.objects.all()
        serializer = PostViewSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SendOtp(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = None
            otp = generate_otp()
            
            if 'email' in data:
                user = UserData.objects.filter(email=data['email']).first()
                OTPVerification.objects.update_or_create(user=user, defaults={'otp': otp, 'email': data['email']})
                # Send OTP via email
                send_mail_otp(data['email'], otp)
                return Response({'message': 'OTP sent to the email address.'}, status=status.HTTP_200_OK)

            elif 'phone' in data:
                user = UserData.objects.filter(phone=data['phone']).first()
                OTPVerification.objects.update_or_create(user=user, defaults={'otp': otp, 'phone_number': data['phone']})
                # Send OTP via SMS
                send_otp(data['phone'], otp)
                return Response({'message': 'OTP sent to the mobile number.'}, status=status.HTTP_200_OK)

            return Response({'error': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)