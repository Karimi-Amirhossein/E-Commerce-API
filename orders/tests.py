from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from products.models import Product, Category
from orders.models import Cart, CartItem
from decimal import Decimal
from django.utils import timezone

User = get_user_model()


class CartAPITests(APITestCase):
    """Integration tests for the Cart API."""

    def setUp(self):
        self.user = User.objects.create_user(username="ali", email="tsat@gmail.com", password="123456")
        self.other_user = User.objects.create_user(username="other", email="ali@gmail.com", password="123456")

        self.category = Category.objects.create(name="Electronics")
        self.product1 = Product.objects.create(
            category=self.category,
            name="Laptop",
            price=Decimal("1500.00"),
            stock=10
        )
        self.product2 = Product.objects.create(
            category=self.category,
            name="Mouse",
            price=Decimal("50.00"),
            stock=20
        )

        self.client.force_authenticate(user=self.user)
        self.cart = Cart.objects.create(user=self.user)

    # ------------------------ EXISTING TESTS ------------------------
    def test_add_item_to_cart(self):
        url = reverse("cart:cart-add-item")
        data = {"product_id": self.product1.id, "amount": 2}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.count(), 1)
        item = CartItem.objects.first()
        self.assertEqual(item.product, self.product1)
        self.assertEqual(item.amount, 2)

    def test_increase_quantity_if_item_exists(self):
        CartItem.objects.create(cart=self.cart, product=self.product1, amount=1)
        url = reverse("cart:cart-add-item")
        response = self.client.post(url, {"product_id": self.product1.id, "amount": 3}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = CartItem.objects.get(cart=self.cart, product=self.product1)
        self.assertEqual(item.amount, 4)

    def test_view_cart(self):
        CartItem.objects.create(cart=self.cart, product=self.product1, amount=1)
        CartItem.objects.create(cart=self.cart, product=self.product2, amount=2)

        url = reverse("cart:cart-detail", kwargs={"id": self.cart.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 2)

    def test_remove_item_from_cart(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product2, amount=1)
        url = reverse("cart:cart-item-detail", kwargs={"cart_id": self.cart.id, "item_id": item.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CartItem.objects.filter(id=item.id).exists())

    def test_pay_cart(self):
        CartItem.objects.create(cart=self.cart, product=self.product1, amount=1)
        CartItem.objects.create(cart=self.cart, product=self.product2, amount=2)

        url = reverse("cart:cart-pay", kwargs={"id": self.cart.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cart.refresh_from_db()
        self.assertTrue(self.cart.is_payed)
        self.assertEqual(self.cart.total_payed, Decimal("1600.00"))
        self.assertIsNotNone(self.cart.pay_date)

    def test_user_cannot_access_others_cart(self):
        self.client.logout()
        self.client.force_authenticate(user=self.other_user)
        
        url = reverse("cart:cart-detail", kwargs={"id": self.cart.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ------------------------ ADDITIONAL TESTS ------------------------
    # AddItemToCart edge cases
    def test_add_invalid_product_id(self):
        url = reverse("cart:cart-add-item")
        response = self.client.post(url, {"product_id": 9999, "amount": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_negative_or_zero_amount(self):
        url = reverse("cart:cart-add-item")
        response = self.client.post(url, {"product_id": self.product1.id, "amount": 0}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url, {"product_id": self.product1.id, "amount": -5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_item_to_others_cart(self):
        other_cart = Cart.objects.create(user=self.other_user)
        url = reverse("cart:cart-add-item")
        response = self.client.post(url, {"cart_id": other_cart.id, "product_id": self.product1.id, "amount": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_add_item_to_paid_cart(self):

        self.cart.is_payed = True
        self.cart.save()
        url = reverse("cart:cart-add-item")
        response = self.client.post(url, {
            "cart_id": self.cart.id,  
            "product_id": self.product1.id,
            "amount": 1
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    # UpdateCartItem edge cases
    def test_update_nonexistent_item(self):
        url = reverse("cart:cart-item-detail", kwargs={"cart_id": self.cart.id, "item_id": 999})
        response = self.client.patch(url, {"amount": 5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item_in_others_cart(self):
        other_cart = Cart.objects.create(user=self.other_user)
        other_item = CartItem.objects.create(cart=other_cart, product=self.product1, amount=1)
        url = reverse("cart:cart-item-detail", kwargs={"cart_id": other_cart.id, "item_id": other_item.id})
        response = self.client.patch(url, {"amount": 5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # CartDetail edge cases
    def test_view_nonexistent_cart(self):
        url = reverse("cart:cart-detail", kwargs={"id": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_item_subtotal_calculation(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product1, amount=3)
        url = reverse("cart:cart-detail", kwargs={"id": self.cart.id})
        response = self.client.get(url)
        self.assertEqual(Decimal(response.data["items"][0]["subtotal"]), item.product.price * item.amount)

    def test_cart_total_calculation(self):
        CartItem.objects.create(cart=self.cart, product=self.product1, amount=2)
        CartItem.objects.create(cart=self.cart, product=self.product2, amount=3)
        url = reverse("cart:cart-detail", kwargs={"id": self.cart.id})
        response = self.client.get(url)
        total = sum(Decimal(i["subtotal"]) for i in response.data["items"])
        self.assertEqual(Decimal(response.data["subtotal"]), total)


    # PayCart edge cases
    def test_pay_cart_twice(self):
        CartItem.objects.create(cart=self.cart, product=self.product1, amount=1)
        url = reverse("cart:cart-pay", kwargs={"id": self.cart.id})
        self.client.post(url)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pay_empty_cart(self):
        empty_cart = Cart.objects.create(user=self.user)
        url = reverse("cart:cart-pay", kwargs={"id": empty_cart.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pay_cart_non_owner(self):
        self.client.logout()
        self.client.force_authenticate(user=self.other_user)
        url = reverse("cart:cart-pay", kwargs={"id": self.cart.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Authentication tests
    def test_access_without_authentication(self):
        self.client.logout()
        url = reverse("cart:cart-add-item")
        response = self.client.post(url, {"product_id": self.product1.id, "amount": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        url = reverse("cart:cart-detail", kwargs={"id": self.cart.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
