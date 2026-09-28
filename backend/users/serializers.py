from rest_framework import serializers
from .models import UserProfile , Category, Product, CartItem, Cart
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'description', 'price', 'image', 'image_url', 'created_at']   

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            # return relative URL (e.g. /media/...) so frontend can prefix BASE_URL
            return obj.image.url
        return None
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']   
        
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) 
    class Meta:
        model = UserProfile
        fields = ['id', 'name', 'age', 'height', 'weight', 'image', 'user', 'address', 'phone_number', 'birth_date', 'weekly_score', 'monthly_score', 'is_banned']
        
        
class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    

    class Meta:
        model = CartItem
        fields = '__all__'
        
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField(source='total_price')

    class Meta:
        model = Cart
        fields = '__all__'
