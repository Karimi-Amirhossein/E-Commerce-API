from rest_framework import status, views, generics, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.apps import apps

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, AddItemSerializer, UpdateItemSerializer
from .permissions import IsCartOwner

Product = apps.get_model('products', 'Product')


class CartDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/orders/carts/<id>/
    Retrieve the current user's cart (only accessible by the owner).
    """
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated, IsCartOwner]
    lookup_url_kwarg = 'id'


class AddItemToCartView(views.APIView):
    """
    POST /api/v1/orders/carts/add-item/
    Adds a product to the current user's cart or increases quantity if it exists.
    Creates a cart if one doesn't exist.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data.get('quantity', 1)

        product = get_object_or_404(Product.objects.select_for_update(), pk=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)

        with transaction.atomic():
            item, created = CartItem.objects.select_for_update().get_or_create(
                cart=cart, product=product, defaults={'quantity': quantity}
            )

            if not created:
                item.quantity += quantity
                item.save()
                detail_message = "Product quantity updated in cart."
                status_code = status.HTTP_200_OK
            else:
                detail_message = "Product added to cart."
                status_code = status.HTTP_201_CREATED

            item.refresh_from_db()
            item_serializer = CartItemSerializer(item)
            return Response(
                {"detail": detail_message, "item": item_serializer.data},
                status=status_code
            )


class UpdateCartItemView(views.APIView):
    """
    PATCH /api/v1/orders/carts/<cart_id>/items/<item_id>/
        Updates item quantity (if 0 → delete).
    DELETE /api/v1/orders/carts/<cart_id>/items/<item_id>/
        Removes the item from cart.
    """
    permission_classes = [permissions.IsAuthenticated, IsCartOwner]

    def get_object(self, cart_id, item_id, user):
        cart = get_object_or_404(Cart, pk=cart_id, user=user)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        self.check_object_permissions(self.request, cart)
        return cart, item

    def patch(self, request, cart_id, item_id):
        cart, item = self.get_object(cart_id, item_id, request.user)
        serializer = UpdateItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_quantity = serializer.validated_data['quantity']

        if new_quantity <= 0:
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        item.quantity = new_quantity
        item.save()
        item.refresh_from_db()
        item_serializer = CartItemSerializer(item)
        return Response(
            {"detail": "Item quantity updated.", "item": item_serializer.data},
            status=status.HTTP_200_OK
        )

    def delete(self, request, cart_id, item_id):
        cart, item = self.get_object(cart_id, item_id, request.user)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)