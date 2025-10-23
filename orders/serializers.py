from rest_framework import serializers
from django.apps import apps
from .models import Cart, CartItem

Product = apps.get_model('products', 'Product')

class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    unit_price = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()

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

    def get_subtotal(self, obj):
        return obj.total_price  # یا Decimal(obj.amount * obj.product.price)

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'subtotal', 'created_at')  # فیلد 'total_payed' حذف شده است
        read_only_fields = ('user', 'created_at')


class UpdateItemSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=0)

class AddItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1, default=1)
