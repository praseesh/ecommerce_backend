from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, Order, Product
from .serializers import CartItemSerializer, OrderSerializer, ProductViewSerializer
from django.shortcuts import get_object_or_404
from users.models import UserData
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

class CartView(APIView):
    def get(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user,is_purchased=False)
        serializer = CartItemSerializer(cart,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']
            try:
                cart, created = Cart.objects.get_or_create(user=user,
                                                           product=product,
                                                            defaults={'quantity': quantity})
                if not created:
                    
                    if cart.quantity + quantity > 5:
                        return Response(
                            {"error": "Adding more than 5 items for the same product is not allowed."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    cart.quantity += quantity
                    
                    cart.save()
                return Response(
                    {'message': 'Product added to cart successfully.'},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {"error": f"An error occurred: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
    def delete(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(Cart, cart=cart, product__id=product_id)
        cart_item.delete()
        return Response({'message': 'Item removed from cart'}, status=status.HTTP_200_OK)
    

    


