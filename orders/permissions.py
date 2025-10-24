from rest_framework import permissions


class IsCartOwner(permissions.BasePermission):
    """
    Custom permission to allow only the owner of the cart
    (or items within it) to access or modify it.
    """

    def has_permission(self, request, view):
        """
        Ensures that the user is authenticated before any object-level checks.
        This prevents anonymous users from reaching has_object_permission.
        """
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check:
        - If obj is a Cart → must belong to the requesting user.
        - If obj is a CartItem → its cart must belong to the requesting user.
        """
        user = request.user

        # Handle both Cart and CartItem types gracefully
        if hasattr(obj, "user"):
            return obj.user == user
        if hasattr(obj, "cart") and hasattr(obj.cart, "user"):
            return obj.cart.user == user

        # Explicitly deny if object type is unexpected
        return False