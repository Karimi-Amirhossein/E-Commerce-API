from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer
from products.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for individual cart items.
    Shows detailed product info (read) and allows adding items via product_id (write).
    """

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True,
        required=False
    )
    product = ProductSerializer(read_only=True)
    unit_price = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ('id', 'product_id', 'product', 'quantity', 'unit_price', 'total_price')


class CartSerializer(serializers.ModelSerializer):
    """Serializer for the user's cart."""
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_price', 'created_at')
        read_only_fields = ('created_at',)


class AddItemSerializer(serializers.Serializer):
    """Used for adding a product to cart."""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateItemSerializer(serializers.Serializer):
    """Used for updating item quantity in the cart."""
    quantity = serializers.IntegerField(min_value=0)