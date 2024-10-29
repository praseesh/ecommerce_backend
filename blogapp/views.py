from django.core.mail import send_mail
from .models import OTPVerification, Posts
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from blogapp.tasks import send_welcome_email
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import OTPVerification, UserData,TemporaryUserRegistration
from .serializers import OTPRequestSerializer, OTPVerifySerializer,UserDataSerializer, PostViewSerializer
from .utils import send_otp,generate_otp,send_mail_otp
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
                    'password': make_password(request.data['password']),
                    'otp': otp,
                }
            )
            email = request.data.get('email')
            phone = request.data.get('phone')
            OTPVerification.objects.update_or_create(email=email, defaults={'otp': otp, 'phone_number': phone})
            if email:
                send_mail_otp(email, otp)
            # if phone:
            #     send_otp(phone, otp)
            return Response(
                {'message': 'User registration initiated.\
                    An OTP has been sent to your email \
                        and phone for verification.'},
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
                    user = user_serializer.save(is_active=True)
                    temp_user.delete() 
                    return Response({'message': 'OTP verified and user created successfully'}, status=status.HTTP_200_OK)
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
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

class SendOtp(APIView):
    pass
#     def post(self, request, *args, **kwargs):
#         serializer = OTPRequestSerializer(data=request.data)
#         if serializer.is_valid():
#             data = serializer.validated_data
#             user = None
#             otp = generate_otp()
#             if 'email' in data:
#                 user = UserData.objects.filter(email=data['email']).first()
#                 OTPVerification.objects.update_or_create(user=user, defaults={'otp': otp, 'email': data['email']})
#                 send_mail_otp(data['email'], otp)
#                 return Response({'message': 'OTP sent to the email address.'}, status=status.HTTP_200_OK)

#             elif 'phone' in data:
#                 user = UserData.objects.filter(phone=data['phone']).first()
#                 OTPVerification.objects.update_or_create(user=user, defaults={'otp': otp, 'phone_number': data['phone']})
#                 send_otp(data['phone'], otp)
#                 return Response({'message': 'OTP sent to the mobile number.'}, status=status.HTTP_200_OK)

#             return Response({'error': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostView(APIView):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        posts = Posts.objects.all()
        serializer = PostViewSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


def send_wel(request): 
    send_welcome_email.delay("prameepramee0@gmail.com")
    return HttpResponse("Welcome email has been sent!")