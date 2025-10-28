from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    
    path("api/v1/users/", include("users.urls", namespace="users")),  # Route all user-related API endpoints to the users app
    path('api/v1/', include('products.urls')),  # Route all product-related API endpoints to the products app
    path("api/v1/orders/", include("orders.urls", namespace="orders")), # Route all order-related API endpoints to the orders app
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),  # Endpoint for API schema generation
    path('api/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'), # Swagger UI for API documentation
]
