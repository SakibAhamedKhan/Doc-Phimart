from rest_framework import serializers
from decimal import Decimal
from product.models import Category, Product, Review, ProductImage
from django.contrib.auth import get_user_model

# class CategorySerializers(serializers.Serializer):
#     id = serializers.IntegerField()
#     name = serializers.CharField()
#     description = serializers.CharField()

class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields =  ['name', 'description', 'product_count']
        
    product_count = serializers.IntegerField(required=False)

# class ProductSerializers(serializers.Serializer):
#     id = serializers.IntegerField()
#     name = serializers.CharField()
#     unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, source='price')
    
#     price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    
#     category = serializers.PrimaryKeyRelatedField(
#         queryset = Category.objects.all()
#     )
#     category_str = serializers.StringRelatedField(source="category")
#     category_all = CategorySerializers(source='category')
#     category_all2 = serializers.HyperlinkedRelatedField(
#         queryset = Category.objects.all(),
#         view_name = 'view-specific-category', 
#         source='category'
#     )
    
#     def calculate_tax(self, product):
#         return round(product.price * Decimal(1.1), 2)

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id','image']
        
    def create(self, validated_data):
        product_id = self.context['product_id']
        productImage = ProductImage.objects.create(product_id=product_id, **validated_data)
        return productImage

class ProductSerializers(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'category', 'price_with_tax', 'category_all2', 'images']
        
    category_all2 = serializers.HyperlinkedRelatedField(
        queryset = Category.objects.all(),
        view_name = 'category-detail', 
        source='category'
    )
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    
    def calculate_tax(self, product):
        return round(product.price * Decimal(1.1), 2)
    
    def validate_price(self, price):
        if price < 0 : 
            raise serializers.ValidationError('Price could not be negative')
        return price
    
    # def validate(self, attrs):
    #     if attrs['password1'] != attrs['password2']:
    #         raise serializers.ValidationError("Password didn't matched!")
    
    # def create(self, validated_data):
    #     product = Product(**validated_data)
    #     product.other = 1 ## other kono kicu add korte cayle save korar age
    #     product.save()
    

    
class SimpleUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(method_name='get_current_user_name')
    class Meta:
        model = get_user_model()
        fields = ['id', 'name']
        
    def get_current_user_name(self, obj):
        return obj.get_full_name()
    
class ReviewSerializer(serializers.ModelSerializer):
    # user = SimpleUserSerializer(read_only=True)
    user = serializers.SerializerMethodField(method_name='get_user')
    class Meta:
        model = Review
        fields = ['id', 'user', 'comment', 'ratings', 'product']
        read_only_fields = ['user', 'product']
        
    def get_user(self, obj):
        return SimpleUserSerializer(obj.user).data
        
    def create(self, validated_data):
        product_id = self.context['product_id']
        review = Review.objects.create(product_id=product_id, **validated_data)
        return review
        
        