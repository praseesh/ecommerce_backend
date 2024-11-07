from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .serializers import AdminLoginSerializer,UserDataSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from users.models import UserData
from products.models import Product
from .pagination import AdminUserPagination


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
    
    
# class AdminUserCreate(APIView):