from rest_framework import serializers
from .models import CustomUser


class UserRegisterSerializer(serializers.ModelSerializer):          # Serializer for user registration
    password2 = serializers.CharField( 
        write_only=True, 
        style={'input_type': 'password'} 
    )
       
    class Meta:                                  # Meta class to specify model and fields
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True} 
        }

    def validate(self, attrs):
        """Ensure both password fields match."""
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        """Create and return a new user instance."""
        validated_data.pop('password2')
        return CustomUser.objects.create_user(**validated_data)
