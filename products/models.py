from django.db import models 

class Product(models.Model): 
    """Represents a product in the e-commerce store."""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:                                # Meta options for the Product model
        ordering = ['-created_at']
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):                         # String representation of the Product model
        return f"{self.name} (${self.price})"
