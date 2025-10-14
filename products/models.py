from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Represents a category for grouping products."""
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:                  # Meta options for the Category model
        ordering = ['name']
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):         # Override save method to auto-generate slug
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    """Represents a product in the e-commerce store."""
    category = models.ForeignKey(
    Category,
    related_name='products',
    on_delete=models.SET_NULL,
    null=True,
    blank=True)

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
        return f"{self.name} — ${self.price:,.2f}"