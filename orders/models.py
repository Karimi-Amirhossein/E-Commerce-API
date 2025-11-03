from django.db import models
from django.conf import settings
from products.models import Product


# (Enum for Order Status)
class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'
    CANCELLED = 'CANCELLED', 'Cancelled'
    
class Cart(models.Model):
    """Represents a user's shopping cart (one cart per user)."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        """Total price of all items in the cart."""
        # Ensure items exist before summing
        if self.items.exists():
             return sum(item.total_price for item in self.items.all())
        return 0 # Return 0 if cart has no items


    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    """Represents a single product entry in a user's cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    @property
    def unit_price(self):
        return self.product.price if self.product else 0

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def __str__(self):
        product_name = self.product.name if self.product else "N/A"
        return f"{self.quantity} × {product_name}"
    

class Order(models.Model):
    """Represents a finalized customer order."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # Store total price at the time of order creation
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # status = models.CharField(max_length=50, default='Pending')  # optional future field

    status = models.CharField(
        max_length=10, 
        choices=OrderStatus.choices, 
        default=OrderStatus.PENDING
    )
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        # Defensive but still clean
        return f"Order #{self.pk or '?'} by {getattr(self.user, 'username', 'Unknown')}"

class OrderItem(models.Model):
    """Represents an individual product within an order."""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        help_text="Product purchased (protected from deletion if ordered)."
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price at purchase time

    @property
    def total_price(self):
        """Returns total cost for this item."""
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} × {getattr(self.product, 'name', 'Unknown')} (Order #{self.order_id})"
    
class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING   = "PENDING",   "Pending"
        SUCCEEDED = "SUCCEEDED", "Succeeded"
        FAILED    = "FAILED",    "Failed"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.pk} for Order {self.order_id} - {self.status}"