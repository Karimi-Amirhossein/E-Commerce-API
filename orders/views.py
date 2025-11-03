from rest_framework import status, views, generics, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.apps import apps

from .models import Cart, CartItem, OrderStatus, Payment
from .serializers import CartSerializer, CartItemSerializer, AddItemSerializer, UpdateItemSerializer
from .permissions import IsCartOwner
from .models import Order, OrderItem
from .serializers import OrderSerializer, CreatePaymentIntentSerializer, PaymentSerializer
import stripe
from django.conf import settings
# Set the Stripe API key on module load
stripe.api_key = settings.STRIPE_SECRET_KEY

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
    

class CreatePaymentIntentView(views.APIView):
    """
    POST /api/v1/orders/create-payment-intent/
    Creates a Stripe PaymentIntent for a given order belonging to the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreatePaymentIntentSerializer

    def post(self, request, *args, **kwargs):
        # Validate request data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_id = serializer.validated_data['order_id']

        # Retrieve user's pending order
        try:
            order = Order.objects.get(
                pk=order_id,
                user=request.user,
                status=OrderStatus.PENDING
            )
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found or already processed."},
                status=status.HTTP_404_NOT_FOUND
            )

        amount_in_cents = int(order.total_price * 100)

        # Create Payment + Stripe Intent atomically
        with transaction.atomic():
            payment = Payment.objects.create(
                order=order,
                amount=order.total_price,
                status=Payment.Status.PENDING
            )

            try:
                intent = stripe.PaymentIntent.create(
                    amount=amount_in_cents,
                    currency='usd',
                    metadata={
                        'order_id': order.id,
                        'payment_id': payment.id,
                        'user_id': request.user.id
                    }
                )

                payment.stripe_payment_intent_id = intent.id
                payment.save(update_fields=['stripe_payment_intent_id'])

                return Response(
                    {
                        "clientSecret": intent.client_secret,
                        "payment_id": payment.id,
                        "order_id": order.id
                    },
                    status=status.HTTP_201_CREATED
                )

            except stripe.StripeError as e:
                payment.status = Payment.Status.FAILED
                payment.save(update_fields=['status'])
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

            except Exception as e:
                transaction.set_rollback(True)
                return Response(
                    {"detail": "An unexpected error occurred."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            

class StripeWebhookView(views.APIView):
    """
    POST /api/v1/orders/stripe-webhook/
    Webhook endpoint for Stripe payment confirmation.
    This endpoint must be PUBLIC (no authentication).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        endpoint_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", None)

        # Ensure webhook secret is configured
        if not endpoint_secret:
            print("❌ Webhook Error: STRIPE_WEBHOOK_SECRET not configured in settings.py.")
            return Response(
                {"detail": "Webhook secret not configured."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # --- Step 1: Verify Stripe signature ---
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            print(f"❌ Webhook Error: Invalid payload. {e}")
            return Response({"detail": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.SignatureVerificationError as e:
            print(f"❌ Webhook Error: Invalid signature. {e}")
            return Response({"detail": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        # --- Step 2: Handle different Stripe events ---
        event_type = event.get("type")
        payment_intent = event["data"]["object"]
        payment_id = payment_intent.get("metadata", {}).get("payment_id")

        if not payment_id:
            print(f"❌ Webhook Error: payment_id not found in metadata for intent {payment_intent.get('id')}")
            return Response(status=status.HTTP_200_OK)  # Always respond 200 to Stripe

        if event_type == "payment_intent.succeeded":
            self.handle_payment_succeeded(payment_id, payment_intent.get("id"))

        elif event_type == "payment_intent.payment_failed":
            self.handle_payment_failed(payment_id)

        # You can handle more events like 'charge.refunded' here later if needed

        # --- Step 3: Respond success to Stripe ---
        return Response(status=status.HTTP_200_OK)

    # --------------------------------------------------
    # Helper Methods
    # --------------------------------------------------

    def handle_payment_succeeded(self, payment_id, stripe_pi_id):
        """Handles successful payment events."""
        try:
            with transaction.atomic():
                payment = Payment.objects.select_for_update().get(id=payment_id)

                if payment.status == Payment.Status.PENDING:
                    # Update Payment
                    payment.status = Payment.Status.SUCCEEDED
                    payment.stripe_payment_intent_id = stripe_pi_id
                    payment.save(update_fields=["status", "stripe_payment_intent_id"])

                    # Update Order
                    order = payment.order
                    order.status = OrderStatus.COMPLETED
                    order.save(update_fields=["status"])

                    print(f"✅ Payment succeeded for Order {order.id}. Status set to COMPLETED.")
                    # (Optional: trigger email, send notification, etc.)

        except Payment.DoesNotExist:
            print(f"❌ Webhook Error: Payment with ID {payment_id} not found.")
        except Exception as e:
            print(f"❌ Webhook Error (Succeeded): {str(e)}")

    def handle_payment_failed(self, payment_id):
        """Handles failed payment events."""
        try:
            with transaction.atomic():
                payment = Payment.objects.select_for_update().get(id=payment_id)

                if payment.status == Payment.Status.PENDING:
                    # Update Payment
                    payment.status = Payment.Status.FAILED
                    payment.save(update_fields=["status"])

                    # Update Order
                    order = payment.order
                    order.status = OrderStatus.FAILED
                    order.save(update_fields=["status"])

                    print(f"❌ Payment failed for Order {order.id}. Status set to FAILED.")
                    # (Optional: restore stock, send notification, etc.)

        except Payment.DoesNotExist:
            print(f"❌ Webhook Error: Payment with ID {payment_id} not found.")
        except Exception as e:
            print(f"❌ Webhook Error (Failed): {str(e)}")