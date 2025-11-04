from django.contrib import admin
from .models import Product, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for the Category model."""
    
    # Display these fields in the list view
    list_display = ("name", "slug")
    
    # Enable search by category name
    search_fields = ("name",)
    
    # Auto-generate slug from the name
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for the Product model."""
    
    # Columns displayed in the list view
    list_display = ("name", "price", "stock", "category", "updated_at")
    
    # Filters shown in the right sidebar
    list_filter = ("category", "updated_at")
    
    # Enable search by name and description
    search_fields = ("name", "description")
    
    # Optional: group fields in the form view
    fieldsets = (
        ("Basic Info", {"fields": ("name", "category", "description")}),
        ("Pricing & Stock", {"fields": ("price", "stock")}),
        ("Metadata", {"fields": ("updated_at",)}),
    )
    
    # Make 'updated_at' read-only
    readonly_fields = ("updated_at",)
