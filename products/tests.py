from django.test import TestCase
from decimal import Decimal
from rest_framework.test import APIClient
from django.urls import reverse
from products.models import Product
from django.contrib.auth import get_user_model
 



class ProductAPITests(TestCase):
    """Integration tests for Product API endpoints."""

    def setUp(self):
        """Initialize test data and API client."""
        self.client = APIClient()
        User= get_user_model()
        self.user = User.objects.create_user(username='testuser',email='test@gmail.com', password='12345')
        self.client.force_authenticate(user=self.user)

        self.laptop = Product.objects.create(
            name="Laptop", description="Powerful laptop", price=1500.00, stock=10
        )
        self.phone = Product.objects.create(
            name="Phone", description="Android smartphone", price=700.00, stock=50
        )
        self.headphones = Product.objects.create(
            name="Headphones", description="Noise cancelling", price=200.00, stock=30
        )

        self.list_url = reverse('product-list')


    def test_list_products(self):
        """Should return list of all products"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

    def test_create_product(self):
        """Should create a new product"""
        data = {
            "name": "Tablet",
            "description": "Portable device",
            "price": 300.00,
            "stock": 20
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Product.objects.filter(name="Tablet").exists())

    def test_update_product(self):
        """Should update a product"""
        url = reverse('product-detail', args=[self.laptop.id])
        response = self.client.patch(url, {"name": "Gaming Laptop"}, format='json')
        self.assertEqual(response.status_code, 200)
        self.laptop.refresh_from_db()
        self.assertEqual(self.laptop.name, "Gaming Laptop")

    def test_delete_product(self):
        """Should delete a product"""
        url = reverse('product-detail', args=[self.phone.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Product.objects.filter(id=self.phone.id).exists())


    def test_filter_by_price(self):
        """Should filter products by exact price"""
        response = self.client.get(self.list_url, {'price': 700.00})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Phone")

    def test_search_products(self):
        """Should return products matching search term"""
        response = self.client.get(self.list_url, {'search': 'laptop'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Laptop")

    def test_ordering_by_price(self):
        """Should order products by price ascending"""
        
        response = self.client.get(self.list_url, {'ordering': 'price'})
        self.assertEqual(response.status_code, 200)
        prices = [Decimal(p['price']) for p in response.data]
        self.assertEqual(prices, sorted(prices))