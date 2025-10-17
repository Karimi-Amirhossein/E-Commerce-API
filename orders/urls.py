from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('carts/<int:id>/', views.CartDetailView.as_view(), name='cart-detail'),
    path('carts/add-item/', views.AddItemToCartView.as_view(), name='cart-add-item'),
    path('carts/<int:cart_id>/items/<int:item_id>/', views.UpdateCartItemView.as_view(), name='cart-item-detail'),
    path('carts/<int:id>/pay/', views.PayCartView.as_view(), name='cart-pay'),
]
