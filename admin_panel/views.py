from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .serializers import AdminLoginSerializer,UserDataSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from users.models import UserData
from users.serializers import UserDataSerializer as UDS
from .utils import  send_mail_otp
from products.models import Product
from .pagination import AdminUserPagination
from rest_framework.exceptions import NotFound, PermissionDenied

class AdminLoginView(APIView):
    permission_classes = [AllowAny] 
    
    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminDashboardView(APIView):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user_count = UserData.objects.count()
        product_count = Product.objects.count()
        last_10_users = UserData.objects.all().order_by('-id')[:10]
        users_data =[
            {
            'user_id' : user.id,
            'username' : user.username,
            'email' : user.email,
            'phone': user.phone,
            'is_active': user.is_active
        }
            for user in last_10_users
            ]
        last_10_products = Product.objects.all().order_by('-id')[:10]
        products_data = [
            {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'stock_quantity': product.stock_quantity
            }
            for product in last_10_products
        ]
        return Response({
            'message' : 'Welcome to Admin Dashboard',
            'user_count': user_count,
            'product_count': product_count,
            'last_10_users': users_data,
            'last_10_products': products_data
        }, status=200)
        
class AdminUserView(generics.ListAPIView):
    queryset = UserData.objects.all().order_by('-id')  
    serializer_class = UserDataSerializer
    pagination_class = AdminUserPagination
    
    
class AdminUserCreate(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UDS(data=request.data)
        if serializer.is_valid():
            welcome_message = "User Registration Successful"
            email = request.data.get('email')
            username = request.data.get('username')
            if email and username:
               
                send_mail_otp(email, welcome_message)
                return Response(
                    {'message': f'User registration initiated. A welcome email has been sent to {username}.' },
                    status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'message': 'Email or Username missing.'},
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class DeleteProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def delete(self, request, user_id, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action.")

        try:
            user = UserData.objects.get(id=user_id)
            user.delete()  
            return Response(
                {'message': 'User profile deleted successfully.'},
                status=status.HTTP_204_NO_CONTENT)
        except UserData.DoesNotExist:
            raise NotFound("User not found.")