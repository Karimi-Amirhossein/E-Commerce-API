from django.shortcuts import render, get_object_or_404
from django.db import transaction
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

        # Fetch the product based on product_id
        product = get_object_or_404(Product, id=product_id)

        # If cart_id is provided, get the cart, else create a new cart
        if cart_id:
            cart = get_object_or_404(Cart, pk=cart_id, user=request.user)
        else:
            cart, created = Cart.objects.get_or_create(user=request.user)
        
        with transaction.atomic():
            item, created = CartItem.objects.select_for_update().get_or_create(cart=cart, product=product)
            
            if created:
                item.amount = amount
                item.save()
                item_ser = CartItemSerializer(item, context={'request': request})
                return Response(
                    {'detail': 'Product added to cart.', 'item': item_ser.data},
                    status=status.HTTP_201_CREATED
                )
            
            # Item exists, so increase the amount
            item.amount += amount
            item.save()
            item_ser = CartItemSerializer(item, context={'request': request})
            return Response(
                {'detail': 'The number of items in the cart increased.', 'item': item_ser.data},
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
        self.check_object_permissions(request, cart)  # Check if the user is the owner
       
        ser = UpdateItemSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        amount = ser.validated_data['amount']
        
        if amount == 0:
            item.delete()
            return Response({'detail': 'Item deleted.'}, status=status.HTTP_204_NO_CONTENT)
        
        item.amount = amount
        item.save()
        return Response({'detail': 'The value was updated.', 'item': CartItemSerializer(item).data})

    def delete(self, request, cart_id, item_id):
        cart, item = self.get_item(cart_id, item_id)
        self.check_object_permissions(request, cart)
        item.delete()
        return Response({'detail': 'Item deleted'}, status=status.HTTP_204_NO_CONTENT)
