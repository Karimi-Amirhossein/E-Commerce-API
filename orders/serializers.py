from rest_framework import serializers
from django.apps import apps
from .models import Cart, CartItem

Product = apps.get_model('products', 'Product')

class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    unit_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()  

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'amount', 'unit_price', 'total_price', 'subtotal')
        extra_kwargs = {'product_id': {'write_only': True}}

    product_id = serializers.PrimaryKeyRelatedField(
        source='product', queryset=Product.objects.all(), write_only=True
    )

    def get_product(self, obj):
        return {
            'id': obj.product.id,
            'name': getattr(obj.product, 'name', ''),
            'price': getattr(obj.product, 'price', None)
        }

    def get_unit_price(self, obj):
        return obj.unit_price

    def get_total_price(self, obj):
        return obj.total_price

    def get_subtotal(self, obj):
        return obj.total_price  # یا Decimal(obj.amount * obj.product.price)
    

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'subtotal', 'total_payed', 'pay_date', 'is_payed', 'created_at')
        read_only_fields = ('user', 'total_payed', 'pay_date', 'is_payed', 'created_at')

    def get_subtotal(self, obj):
        return obj.subtotal

# Serializer for updating amount (PATCH)
class UpdateItemSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=0)

# Serializer for adding/updating item
class AddItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1, default=1)

