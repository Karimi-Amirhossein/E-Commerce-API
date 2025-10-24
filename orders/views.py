from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import status, views, generics, permissions
from rest_framework.response import Response

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from .permissions import IsCartOwner
from django.apps import apps

Product = apps.get_model('products', 'Product')


class CartDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/orders/carts/<id>/
    Retrieve a user's cart (only accessible by the owner).
    """
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated, IsCartOwner]
    lookup_url_kwarg = 'id'


class AddItemToCartView(views.APIView):
    """
    POST /api/v1/orders/carts/add-item/
    Add a product to the current user's cart.
    If cart doesn't exist, create one automatically.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        cart_id = request.data.get('cart_id')

        # Validate product
        product = get_object_or_404(Product, pk=product_id)

        # Find or create user's cart
        if cart_id:
            cart = get_object_or_404(Cart, pk=cart_id, user=request.user)
        else:
            cart, _ = Cart.objects.get_or_create(user=request.user)

        # Check if product already exists in cart
        with transaction.atomic():
            item, created = CartItem.objects.select_for_update().get_or_create(
                cart=cart, product=product
            )
            if created:
                item.quantity = quantity
                item.save()
                serializer = CartItemSerializer(item)
                return Response(
                    {"detail": "Product added to cart.", "item": serializer.data},
                    status=status.HTTP_201_CREATED
                )
            else:
                item.quantity += quantity
                item.save()
                serializer = CartItemSerializer(item)
                return Response(
                    {"detail": "Product quantity updated in cart.", "item": serializer.data},
                    status=status.HTTP_200_OK
                )


class UpdateCartItemView(views.APIView):
    """
    PATCH /api/v1/orders/carts/<cart_id>/items/<item_id>/
    DELETE /api/v1/orders/carts/<cart_id>/items/<item_id>/
    Update or remove a product from cart.
    """
    permission_classes = [permissions.IsAuthenticated, IsCartOwner]

    def get_item(self, cart_id, item_id):
        cart = get_object_or_404(Cart, pk=cart_id)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        return cart, item

    def patch(self, request, cart_id, item_id):
        cart, item = self.get_item(cart_id, item_id)
        self.check_object_permissions(request, cart)

        new_quantity = int(request.data.get('quantity', 1))
        if new_quantity <= 0:
            item.delete()
            return Response({"detail": "Item removed from cart."}, status=status.HTTP_204_NO_CONTENT)

        item.quantity = new_quantity
        item.save()
        serializer = CartItemSerializer(item)
        return Response({"detail": "Item quantity updated.", "item": serializer.data})

    def delete(self, request, cart_id, item_id):
        cart, item = self.get_item(cart_id, item_id)
        self.check_object_permissions(request, cart)

        item.delete()
        return Response({"detail": "Item removed from cart."}, status=status.HTTP_204_NO_CONTENT)