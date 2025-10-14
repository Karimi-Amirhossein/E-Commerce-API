from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing products.

    Features:
    - Supports filtering by category, price, and stock
    - Allows search by product name and description
    - Supports ordering by price and creation date
    """
    queryset = (
        Product.objects
        .select_related('category')  # Optimize DB queries
        .order_by('-created_at')
    )
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Filtering, Searching, and Ordering setup
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'price', 'stock']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']  # Default ordering


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing product categories.

    Uses slug-based lookup for cleaner, SEO-friendly URLs.
    """
    queryset = (
        Category.objects
        .prefetch_related('products')  # Optimize reverse relationship queries
        .order_by('name')
    )
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
