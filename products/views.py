from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem, Product
from .serializers import CartSerializer, CartItemSerializer
from django.shortcuts import get_object_or_404
from users.models import UserData

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
    
    