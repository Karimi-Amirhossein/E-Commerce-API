from rest_framework import generics 
from .models import CustomUser
from .serializers import UserRegisterSerializer


class UserRegisterView(generics.CreateAPIView):
    """API endpoint for user registration."""
    
    queryset = CustomUser.objects.all() 
    serializer_class = UserRegisterSerializer 
