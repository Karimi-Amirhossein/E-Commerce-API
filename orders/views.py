
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from rest_framework import status, generics, views, permissions
from rest_framework.response import Response

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, AddItemSerializer, UpdateItemSerializer
from .permissions import IsCartOwner
from django.apps import apps

Product = apps.get_model('products', 'Product')

class CartDetailView(generics.RetrieveAPIView):
    """
    GET /apis/carts/<id>/ -- View Cart
    Only the owner can see.
    """
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated, IsCartOwner]
    lookup_url_kwarg = 'id'

class AddItemToCartView(views.APIView):

    """
    POST /apis/carts/add-item/
    body: { "cart_id": optional, "product_id": X, "amount": N }
    If cart_id is not given, a new cart will be created and linked to the user.
    If the item is in the cart, the amount will be incremented.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = AddItemSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        product_id = ser.validated_data['product_id']
        amount = ser.validated_data['amount']
        cart_id = request.data.get('cart_id')

        product = get_object_or_404(Product, pk=product_id)

        if cart_id:
            cart = get_object_or_404(Cart, pk=cart_id)
            if cart.user != request.user:
                return Response({"detail": "شما اجازه‌ی دسترسی به این سبد را ندارید."},status=status.HTTP_403_FORBIDDEN)
        else:
            cart, _ = Cart.objects.get_or_create(user=request.user, is_payed=False)

        if cart.is_payed:
            return Response(
                {'detail': 'این سبد قبلاً پرداخت شده و قابل تغییر نیست.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            item, created = CartItem.objects.select_for_update().get_or_create(cart=cart, product=product)
            if created:
                item.amount = amount
                item.save()
                item_ser = CartItemSerializer(item, context={'request': request})
                return Response(
                    {'detail': 'محصول به سبد اضافه شد.', 'item': item_ser.data},
                    status=status.HTTP_201_CREATED
                )

            # موجود بود — افزایش مقدار و بازگشت 200 OK
            item.amount = item.amount + amount
            item.save()
            item_ser = CartItemSerializer(item, context={'request': request})
            return Response(
                {'detail': 'تعداد آیتم در سبد افزایش یافت.', 'item': item_ser.data},
                status=status.HTTP_200_OK
            )

class UpdateCartItemView(views.APIView):
    """
    PATCH /apis/carts/<cart_id>/items/<item_id>/  -> Change quantity (if amount==0 => delete)
    DELETE /apis/carts/<cart_id>/items/<item_id>/ -> Delete item
    """
    permission_classes = [permissions.IsAuthenticated, IsCartOwner]

    def get_item(self, cart_id, item_id):
        cart = get_object_or_404(Cart, pk=cart_id)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        return cart, item

    def patch(self, request, cart_id, item_id):
        cart, item = self.get_item(cart_id, item_id)
        self.check_object_permissions(request, cart)  # بررسی مالکیت
        if cart.is_payed:
            return Response({'detail': 'این سبد قبلاً پرداخت شده و قابل تغییر نیست.'}, status=status.HTTP_400_BAD_REQUEST)

        ser = UpdateItemSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        amount = ser.validated_data['amount']
        if amount == 0:
            item.delete()
            return Response({'detail': 'آیتم حذف شد.'}, status=status.HTTP_204_NO_CONTENT)
        item.amount = amount
        item.save()
        return Response({'detail': 'مقدار به‌روزرسانی شد.', 'item': CartItemSerializer(item).data})

    def delete(self, request, cart_id, item_id):
        cart, item = self.get_item(cart_id, item_id)
        self.check_object_permissions(request, cart)
        if cart.is_payed:
            return Response({'detail': 'این سبد قبلاً پرداخت شده و قابل تغییر نیست.'}, status=status.HTTP_400_BAD_REQUEST)
        item.delete()
        return Response({'detail': 'آیتم حذف شد.'}, status=status.HTTP_204_NO_CONTENT)

class PayCartView(views.APIView):
    """
    POST /apis/carts/<id>/pay/
    Making a simulated payment: total_payed = subtotal, is_payed=True, pay_date=now
    Only the owner is allowed. If the cart is empty or has already been paid, it will throw an error.
    """
    permission_classes = [permissions.IsAuthenticated, IsCartOwner]

    def post(self, request, id):
        cart = get_object_or_404(Cart, pk=id)
        self.check_object_permissions(request, cart)
        if cart.is_payed:
            return Response({'detail': 'این سبد قبلاً پرداخت شده.'}, status=status.HTTP_400_BAD_REQUEST)
        subtotal = cart.subtotal
        if not subtotal:
            return Response({'detail': 'سبد خالی است.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            cart.total_payed = subtotal
            cart.is_payed = True
            cart.pay_date = timezone.now()
            cart.save(update_fields=['total_payed', 'is_payed', 'pay_date'])

        return Response({'detail': 'پرداخت ثبت شد.', 'cart_id': cart.id, 'total_payed': cart.total_payed, 'pay_date': cart.pay_date})
