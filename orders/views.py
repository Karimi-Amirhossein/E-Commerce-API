from rest_framework import status, views, generics, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.apps import apps

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, AddItemSerializer, UpdateItemSerializer
from .permissions import IsCartOwner
from .models import Order, OrderItem
from .serializers import OrderSerializer

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
    POST /api/v1/orders/add-to-cart/
    Adds a product to the user's cart or updates its quantity.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data.get('quantity', 1)

        try:
            with transaction.atomic():
                product = Product.objects.select_for_update().get(pk=product_id)

                cart, _ = Cart.objects.get_or_create(user=request.user)

                item, created = CartItem.objects.select_for_update().get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': quantity}
                )

                if created:
                    detail_message = "Product added to cart."
                    status_code = status.HTTP_201_CREATED
                else:
                    item.quantity += quantity
                    item.save(update_fields=['quantity'])
                    detail_message = "Product quantity updated in cart."
                    status_code = status.HTTP_200_OK

                item.refresh_from_db()
                item_serializer = CartItemSerializer(item)

            return Response(
                {"detail": detail_message, "item": item_serializer.data},
                status=status_code
            )

        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"❌ Error adding item to cart: {e}")
            return Response(
                {"detail": "An internal error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
    
class PlaceOrderView(views.APIView):
    """
    POST /api/v1/orders/place-order/
    Converts the current user's active cart into a finalized order.
    Clears the cart after successful order placement.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            cart = Cart.objects.prefetch_related('items__product').get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {"detail": "No active cart found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not cart.items.exists():
            return Response(
                {"detail": "Cannot place an order with an empty cart."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    total_price=cart.total_price
                )

                order_items = [
                    OrderItem(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.unit_price
                    )
                    for item in cart.items.all()
                ]

                OrderItem.objects.bulk_create(order_items)

                cart.items.all().delete()

        except Exception as e:
            print(f"❌ Error placing order: {e}")
            return Response(
                {"detail": "An error occurred while placing the order."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class OrderHistoryView(generics.ListAPIView):
    """Returns the authenticated user's order history."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)