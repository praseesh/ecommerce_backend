from django.core.mail import send_mail
from admin_panel.pagination import AdminUserPagination
from products.models import Cart, Product
from products.serializers import  OrderSerializer, ProductViewSerializer
from .models import OTPVerification, Posts, UserPayment
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
from django.db import transaction


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

class CreateRazorPayPaymentPage(APIView):
    def post(self,request,*args, **kwargs):
        user = request.user
        unpaid_order = Order.objects.filter(user=user, is_paid=False)
        total_amount = unpaid_order.aggregate(total_amount_to_pay=Sum('total_price'))['total_amount_to_pay']
        if not total_amount:
            return Response({'error':'No Unpaid Orders Found'}, status=status.HTTP_404_NOT_FOUND)
        total_amount_in_paisa = int(total_amount * 100)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            razorpay_order = client.order.create({
                "amount": total_amount_in_paisa,
                "currency": "INR",
                "receipt": f"order_recptid_{user.id}",
                "notes": {"user_id": user.id},
            })
            user_payment = UserPayment.objects.create(
                user=user,
                razorpay_order_id=razorpay_order['id'],
                total_amount=total_amount,
            )
            return Response({
                "order_id": razorpay_order['id'],
                "amount": total_amount,
                "currency": "INR",
                "notes": razorpay_order['notes']
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
"""                                            O R D E R                                                      """
        
class OrderCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        address_id = serializer.validated_data.get('address_id')
        payment_method = serializer.validated_data.get('payment_method')
        is_cart = serializer.validated_data.get('is_cart')

        if is_cart:
            try:
                with transaction.atomic():
                    cart_items = Cart.objects.filter(user=request.user, is_purchased=False)
                    order_items = []
                    total_price = 0
                    for cart_item in cart_items:
                        product = cart_item.product
                        item_total_price = product.price * cart_item.quantity if product.price else 0
                        total_price += item_total_price
                        order = Order(
                            user=request.user,
                            address_id=address_id,
                            product=product,
                            qty=cart_item.quantity,
                            product_price=product.price,
                            total_price=item_total_price,
                            payment_method=payment_method
                        )
                        order_items.append(order) 
                    
                    Order.objects.bulk_create(order_items)
                    cart_items.update(is_purchased=True)
                    return Response({"message": "Order created successfully."}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if not is_cart:
            product_id = serializer.validated_data.get('product_id')  
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'error': 'Given product Not exist'}, status=status.HTTP_404_NOT_FOUND)
            quantity = serializer.validated_data.get('qty', 1)  
            total_price = product.price * quantity if product.price else 0
            order_items = []
            order = Order(
                user=request.user,
                address_id=address_id,
                product=product,
                product_price=product.price,
                qty = quantity,
                total_price=total_price,
                payment_method=payment_method
            )
            order_items.append(order)
            Order.objects.bulk_create(order_items) 
            return Response({"message": "Order created successfully."}, status=status.HTTP_201_CREATED)
    
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
        
from django.db.models import Sum

class UnpaidOrdersTotalView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user  
        unpaid_orders = Order.objects.filter(user=user, is_paid=False)

        order_details = unpaid_orders.values('product_id', 'qty', 'total_price')
        total_amount = unpaid_orders.aggregate(total_amount_to_pay=Sum('total_price'))['total_amount_to_pay']
        
        if total_amount is None:
            total_amount = 0  

        return Response({
            "total_amount_to_pay": total_amount,
            "order_details": list(order_details)
        }, status=status.HTTP_200_OK)
