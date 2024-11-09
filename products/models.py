from django.db import models
from users.models import UserData

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'cart'
    def __str__(self):
        return f"{self.user.username}'s Cart"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    class Meta:
        db_table = 'cart_item'
    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.product.price