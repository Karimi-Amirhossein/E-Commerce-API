from django.urls import path
from . import views
from .views import PlaceOrderView
from .views import OrderHistoryView
app_name = 'orders'

urlpatterns = [
    # Cart URLs
    path('carts/<int:id>/', views.CartDetailView.as_view(), name='cart-detail'),
    path('carts/add-item/', views.AddItemToCartView.as_view(), name='cart-add-item'),
    path('carts/<int:cart_id>/items/<int:item_id>/', views.UpdateCartItemView.as_view(), name='cart-item-detail'),
    # Order URL
    path('place-order/', PlaceOrderView.as_view(), name='place-order'),
    path('history/', OrderHistoryView.as_view(), name='order-history'),
]
