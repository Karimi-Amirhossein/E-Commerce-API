from django.contrib import admin
from .models import Order, OrderItem, Payment, Cart, CartItem


class OrderItemInline(admin.TabularInline):
    """Inline configuration to display OrderItems inside the Order detail page."""
    model = OrderItem
    extra = 0  # No empty rows by default
    readonly_fields = ("product", "price", "quantity")  # These should not be editable
    can_delete = False  # Prevent accidental deletion


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for the Order model."""
    list_display = ("id", "user", "status", "total_price", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "user__username")
    inlines = [OrderItemInline]
    readonly_fields = ("user", "total_price", "created_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    # Allow editing status directly from the list view
    list_editable = ("status",)

    # Optional: prevent saving if user tries to edit read-only fields manually
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing order
            return ("user", "total_price", "created_at")
        return ()

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for the Payment model."""
    list_display = (
        "id",
        "order",
        "status",
        "amount",
        "stripe_payment_intent_id",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("order__id", "stripe_payment_intent_id")
    readonly_fields = (
        "order",
        "amount",
        "status",
        "stripe_payment_intent_id",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin configuration for the Cart model."""
    list_display = ("id", "user", "created_at")
    search_fields = ("user__username",)
    readonly_fields = ("user", "created_at")
    ordering = ("-created_at",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin configuration for the CartItem model."""
    list_display = ("id", "cart", "product", "quantity")
    search_fields = ("cart__id", "product__name")
    list_filter = ("product",)