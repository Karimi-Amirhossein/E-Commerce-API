from django.urls import path
from .views import UserRegisterView

app_name = "users" # Namespace for the users app

urlpatterns = [ 
    path("register/", UserRegisterView.as_view(), name="register"),    # User registration endpoint
]