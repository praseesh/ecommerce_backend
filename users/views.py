from django.core.mail import send_mail
from admin_panel.pagination import AdminUserPagination
from products.models import Cart, Product
from products.serializers import  OrderSerializer, ProductViewSerializer
from .models import OTPVerification, Posts
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from .models import OTPVerification, UserData,TemporaryUserRegistration
from products.models import Order
from .serializers import OTPRequestSerializer, OTPVerifySerializer,UserDataSerializer, PostViewSerializer, UserLoginSerializer, UserProfileSerializer, UserViewSerializer
from .utils import generate_otp
from .tasks import send_mail_otp_task, send_sms_otp_task
from django.contrib.auth.hashers import make_password
from rest_framework.parsers import MultiPartParser
import razorpay
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view

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
            if phone:
                send_sms_otp_task.delay(phone, otp)
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
    

class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]  

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserDashboard(generics.ListAPIView):
    queryset = Product.objects.all().order_by('-id')  
    serializer_class = ProductViewSerializer
    pagination_class = AdminUserPagination
    

"""                                         R A Z O R P A Y                                                      """

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class CreateRazorpayOrderView(APIView):
    def post(self, request, *args, **kwargs):
        order_id = request.data.get('order_id')
        try:
            order = Order.objects.get(id=order_id, payment_method='razorpay')
        except Order.DoesNotExist:
            return Response({'error': 'Invalid order ID or payment method.'}, status=status.HTTP_400_BAD_REQUEST)

        razorpay_order = client.order.create({
            'amount': int(order.total_price * 100),  
            'currency': 'INR',
            'receipt': f"order_{order.id}"
        })
        return Response({
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': order.total_price
        }, status=status.HTTP_200_OK)
        
class OrderCreateView(APIView):
    # def post(self, request, *args, **kwargs):
    #     serializer = OrderSerializer(data=request.data)
        
    #     if not serializer.is_valid():
    #         return Response(None,status=status.HTTP_400_BAD_REQUEST)
        
    #     is_cart = serializer.get('is_cart')
    #     if is_cart:
    #         address_id = serializer.validated_data.get('address_id')
    #         carts = Cart.objects.filter(is_purchased=False,user=request.user.id)
    #         for cart in carts:
    #             product_id = cart.product.id
    #             product_price = cart.product.
    
            # Fetch all user cart data with is_purchased = false,
            # Use for loop for each cart value and place order for all , product stock --

            # check the qty is 0<qty && 5>=qty
    pass
        
        # if case is fialed that means he is trying to place order without using cart, extract all other fields from serielizer example  product_id,user_id all those field, And validate the stock , after that create a order with the all required fields , make product stock --

        
        # return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
class UpdatePaymentStatusView(APIView):
    def post(self, request, *args, **kwargs):
        order_id = request.data.get('order_id')
        payment_status = request.data.get('payment_status')

        try:
            order = Order.objects.get(id=order_id)
            order.payment.payment_status = payment_status
            order.payment.save()

            if payment_status == 'success':
                order.order_status = 'PAID'
                order.save()

            return Response({'message': 'Payment status updated.'}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_400_BAD_REQUEST)
        
    # req
    
    
    # product_id - 
    # address_id- Required
    # product_price - price of the product
    # qty - qty>=1 && qty<=5
    # payment_method = choices ['razorpay','cod','paypal']
    
    # table 
    
    # user_id
    # product_id
    # address_id
    # qty 
    # total_price
    # payment_method
    # status 
    
    
    # On user Side Need table called address := user_id field is required, User can able to DO CRUD operation on that table