from rest_framework import serializers
from .models import Cart, CartItem, Product, Category

class ProductCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'brand', 'price', 'related_products',
                  'stock_quantity', 'image']
    
    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError('Product name cannot be empty.')
        if len(value) > 255:
            raise serializers.ValidationError("Product name cannot be longer than 255 characters.")
        return value

    def validate_category(self, value):
        if not Category.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Selected category does not exist.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive value.")
        return value

    def validate_stock_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Stock quantity must be greater than zero.")
        return value

    def validate_rating(self, value):
        if value < 0.0 or value > 5.0:
            raise serializers.ValidationError("Rating must be between 0.0 and 5.0.")
        return value
    def validate_image(self, image):
        max_size_mb = 5
        if image.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f"Image size must be less than {max_size_mb} MB.")
        valid_extensions = ['.png', '.jpg', '.jpeg']
        if not any([image.name.lower().endswith(ext) for ext in valid_extensions]):
            raise serializers.ValidationError(f"Supported image formats are: {', '.join(valid_extensions)}")

        return image

    def validate_related_products(self, value):
        if self.instance and self.instance.id in [product.id for product in value.all()]:
            raise serializers.ValidationError("A product cannot be related to itself.")
        return value
class CategoryCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']
        
class ProductViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        
class ProductUpdationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'brand', 'price', 'related_products',
                  'stock_quantity', 'image']
    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError('Product name cannot be empty.')
        if len(value) > 255:
            raise serializers.ValidationError("Product name cannot be longer than 255 characters.")
        return value

    def validate_category(self, value):
        if not Category.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Selected category does not exist.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive value.")
        return value

    def validate_stock_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Stock quantity must be greater than zero.")
        return value

    def validate_rating(self, value):
        if value < 0.0 or value > 5.0:
            raise serializers.ValidationError("Rating must be between 0.0 and 5.0.")
        return value

    def validate_related_products(self, value):
        if self.instance and self.instance.id in [product.id for product in value.all()]:
            raise serializers.ValidationError("A product cannot be related to itself.")
        return value
    

class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']
        
    def validate_quantity(value):
        if value > 5:
            raise serializers.ValidationError("Only 5 items can be added for each product.")
        return value

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']
        