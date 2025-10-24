from django.db import models
from django.conf import settings
from products.models import Product


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
        """Returns the total price of all items in the cart."""
        return sum(item.total_price for item in self.items.all())

    def str(self):
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
        """Unit price of the product."""
        return self.product.price if self.product else 0

    @property
    def total_price(self):
        """Total = unit_price × quantity."""
        return self.unit_price * self.quantity

    def str(self):
        product_name = self.product.name if self.product else "N/A"
        return f"{self.quantity} × {product_name}"