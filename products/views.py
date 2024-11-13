from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem, Product
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, ProductViewSerializer
from django.shortcuts import get_object_or_404
from users.models import UserData
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

class CartView(APIView):
    def get(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product']
            quantity =serializer.validated_data['quantity']
            cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not item_created:
                cart_item.quantity += 1
                cart_item.save()
            else:
                cart_item.quantity = quantity
                cart_item.save()
            return Response({'message':'Product added to cart Successfully'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
    def delete(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product__id=product_id)
        cart_item.delete()
        return Response({'message': 'Item removed from cart'}, status=status.HTTP_200_OK)
    
class ProductListAndFilterAPIView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductViewSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]

    filterset_fields = {
        'category': ['exact'],   
        'price': ['gte', 'lte'], 
        'stock_quantity': ['gte', 'lte'],  
    }
    search_fields = ['name', 'description']
    
    
class CheckoutAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data, context={'request': request})  
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)