from rest_framework import viewsets, permissions, filters
from .models import Product
from .serializers import ProductSerializer
from django_filters.rest_framework import DjangoFilterBackend

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products (CRUD operations) with filter & search.
    """
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filterset_fields = ['price', 'stock']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

