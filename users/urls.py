from django.urls import path
from .views import UserRegisterView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = "users" # Namespace for the users app

urlpatterns = [ 
    path("register/", UserRegisterView.as_view(), name="register"),    # User registration endpoint
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # JWT login endpoint
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # JWT token refresh endpoint

]