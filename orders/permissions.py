from rest_framework import permissions

class IsCartOwner(permissions.BasePermission):
    """
    Allows only the cart owner (cart.user) to view/modify/pay.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # obj can be Cart or CartItem
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'cart'):
            return obj.cart.user == request.user
        return False

