from rest_framework import permissions


class IsCartOwner(permissions.BasePermission):
    """
    Allows only the cart owner (cart.user) to view or modify it.
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'cart'):
            return obj.cart.user == request.user
        return False