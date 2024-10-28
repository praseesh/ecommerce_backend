from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from .models import OTPVerification, Posts
from .serializers import PostViewSerializer, UserDataSerializer, OTPVerifySerializer
from .auth import generate_otp
from .models import UserData    
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class UserRegistrationViews(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserDataSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            otp = generate_otp()
            OTPVerification.objects.update_or_create(user=user, defaults={'otp': otp})
            
            send_mail(
                'Your OTP Verification Code',
                f'Your OTP code is {otp}. It is valid for 5 minutes.',
                'your_email@example.com',
                [user.email],
                fail_silently=False,
            )
            
            return Response(
                {'message': 'User Registration Successful. An OTP has been sent to your email for verification.'},
                status=status.HTTP_201_CREATED
            )
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
    
