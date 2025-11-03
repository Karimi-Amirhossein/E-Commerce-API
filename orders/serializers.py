from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Payment, OrderStatus
from products.serializers import ProductSerializer
from products.models import Product
from .models import Order, OrderItem


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


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for individual items within an order."""
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    total_price = serializers.SerializerMethodField()

    
    class Meta:
        model = OrderItem
        fields = ('id', 'product_id', 'product_name', 'quantity', 'price', 'total_price')
        read_only_fields = fields  

    def get_total_price(self, obj):
        """Return total cost for this item."""
        return obj.quantity * obj.price
    

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for displaying complete order details."""
    user = serializers.StringRelatedField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    # (Add 'status' field to show in API responses)
    status = serializers.CharField(read_only=True, source="get_status_display")

    class Meta:
        model = Order
        fields = ('id', 'user', 'created_at', 'total_price', 'items', 'status')
        read_only_fields = fields

class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for representing Payment instances."""
    
    # Human-readable status (e.g., "Pending" instead of "PENDING")
    status = serializers.CharField(read_only=True, source="get_status_display")

    class Meta:
        model = Payment
        fields = [
            'id',
            'order',
            'amount',
            'status',
            'stripe_payment_intent_id',
            'created_at',
        ]
        read_only_fields = fields  # All fields are read-only here


class CreatePaymentIntentSerializer(serializers.Serializer):
    """Serializer for validating input when creating a payment intent."""
    
    # Only the order ID is required from the client
    order_id = serializers.IntegerField(required=True)