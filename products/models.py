from django.conf import settings
from django.db import models
from users.models import UserData,Address
from decimal import Decimal

"""                                                  PRODUCT                                                  """    

class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'category'
    
class Product(models.Model):
    name = models.CharField(max_length=255,null=False,blank=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False,blank=False, related_name='products')
    description = models.TextField(blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    related_products = models.ManyToManyField('self', blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    number_of_reviews = models.PositiveIntegerField(default=0)
    sold_count = models.PositiveIntegerField(default=0)
    stock_quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'product'
    
"""                                                  CART                                                  """    

class Cart(models.Model):
    user = models.OneToOneField(UserData, on_delete=models.CASCADE, related_name='cart')
    is_purchased = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=1)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'cart'
    def __str__(self):
        return f"{self.user.username}'s Cart"

# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')

#     class Meta:
#         db_table = 'cart_item'
#     def __str__(self):
#         return f"{self.quantity} of {self.product.name}"

#     def get_total_price(self):
#         return self.quantity * self.product.price
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('razorpay', 'Razorpay'),
        ('cod', 'Cash on Delivery'),
        ('paypal', 'PayPal'),
    ]

    user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='orders')
    address= models.ForeignKey(Address,on_delete=models.CASCADE, default=1)  # Assuming address is an integer ID from another table
    product= models.ForeignKey(Product,on_delete=models.CASCADE,default=1)  # Product ID is optional for cart-like orders
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)

    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Optional
    qty = models.PositiveIntegerField(null=True, blank=True, default=1)  # Optional, defaults to 1
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.order_status}"

    def calculate_total_price(self):
        """
        Calculate total price dynamically if product_price and qty are available.
        """
        if self.product_price and self.qty:
            return self.product_price * self.qty
        return self.total_price

# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0.00)

#     def save(self, *args, **kwargs):
#         self.subtotal = self.quantity * self.price
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.product.name} - {self.quantity} pcs"

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_id = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=50)
    paid_at = models.DateTimeField()

    class Meta:
        db_table = 'payment'

    def __str__(self):
        return f"Payment for Order {self.order.id}"
    
    
    # req
    
    # product_id
    # product_price
    # qty
    # payment_method
    
    # table 
    
    # user_id
    # product_id
    # qty 
    # total_price
    # payment_method
    # status 
    