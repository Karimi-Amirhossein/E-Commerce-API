from rest_framework import generics,permissions
from .models import CustomUser
from .serializers import UserRegisterSerializer,UserProfileSerializer


class UserRegisterView(generics.CreateAPIView):
    """API endpoint for user registration."""
    
    queryset = CustomUser.objects.all() 
    serializer_class = UserRegisterSerializer 


class UserProfileView(generics.RetrieveUpdateAPIView):
    """API endpoint for viewing and editing the logged-in user's profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user