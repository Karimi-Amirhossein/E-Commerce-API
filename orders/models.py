
from django.db import models
from django.conf import settings
from django.db import models


class Cart(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)

    
    @property
    def subtotal(self):
        """Total price (before final payment) based on items"""
        total = sum((item.total_price for item in self.items.all()), 0)
        # total may be Decimal if item.total_price is Decimal
        return total

    

class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"CartItem(cart={self.cart_id}, product={self.product_id}, amount={self.amount})"

    @property
    def unit_price(self):
        return getattr(self.product, 'price', 0)

    @property
    def total_price(self):
        return self.unit_price * self.amount
