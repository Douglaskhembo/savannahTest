import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from src.catalog.models import Category, Product
from src.orders.models import Order
from django.contrib.auth import get_user_model

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def category():
    return Category.objects.create(name="Bakery")


@pytest.fixture
def product(category):
    return Product.objects.create(name="Bread", price=50, category=category)


@pytest.fixture
def admin_user():
    return User.objects.create_user(
        email="admin@test.com", password="pass123", role=User.Role.ADMIN, phone="0711111111",
    )


@pytest.fixture
def customer_user():
    return User.objects.create_user(
        email="customer@test.com", password="pass123", role=User.Role.BUYER, phone="0722222222",
    )


@pytest.fixture
def another_customer():
    return User.objects.create_user(
        email="other@test.com", password="pass123", role=User.Role.BUYER, phone="0733333333",
    )


@pytest.fixture
def customer_order(customer_user, product):
    return Order.objects.create(customer=customer_user, status="PENDING")


# ----------------- CATEGORY TESTS -----------------

def test_list_categories(api_client, category):
    url = reverse("category-list")
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data[0]["name"] == "Bakery"


def test_delete_category_with_products_fails(api_client, admin_user, product):
    api_client.force_authenticate(user=admin_user)
    url = reverse("category-detail", args=[product.category.id])
    response = api_client.delete(url)
    assert response.status_code == 400
    assert "Cannot delete category" in response.data["detail"]


def test_delete_category_without_products(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    cat = Category.objects.create(name="Produce")
    url = reverse("category-detail", args=[cat.id])
    response = api_client.delete(url)
    assert response.status_code == 204


# ----------------- PRODUCT TESTS -----------------

def test_list_products(api_client, product):
    url = reverse("product-list")
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data[0]["name"] == "Bread"


def test_average_price_no_category(api_client):
    url = reverse("product-average-price")
    response = api_client.get(url)
    assert response.status_code == 400
    assert "category_id required" in response.data["detail"]


def test_average_price_invalid_category(api_client):
    url = reverse("product-average-price")
    response = api_client.get(url, {"category_id": 999})
    assert response.status_code == 404
    assert "category not found" in response.data["detail"]


def test_average_price_success(api_client, category):
    Product.objects.create(name="Cookie", price=100, category=category)
    Product.objects.create(name="Cake", price=200, category=category)

    url = reverse("product-average-price")
    response = api_client.get(url, {"category_id": category.id})
    assert response.status_code == 200
    assert response.data["category"] == "Bakery"
    assert response.data["average_price"] == pytest.approx(150.0)


# ----------------- PERMISSION TESTS -----------------

def test_admin_can_access_any_user(api_client, admin_user, customer_user):
    api_client.force_authenticate(user=admin_user)
    url = reverse("user-detail", args=[customer_user.id])
    response = api_client.get(url)
    assert response.status_code == 200


def test_user_can_access_self_but_not_others(api_client, customer_user, another_customer):
    api_client.force_authenticate(user=customer_user)

    url = reverse("user-detail", args=[customer_user.id])
    response = api_client.get(url)
    assert response.status_code == 200

    url = reverse("user-detail", args=[another_customer.id])
    response = api_client.get(url)
    assert response.status_code == 403


def test_admin_can_access_any_order(api_client, admin_user, customer_order):
    api_client.force_authenticate(user=admin_user)
    url = reverse("order-detail", args=[customer_order.id])
    response = api_client.get(url)
    assert response.status_code == 200


def test_customer_can_access_own_order(api_client, customer_user, customer_order):
    api_client.force_authenticate(user=customer_user)
    url = reverse("order-detail", args=[customer_order.id])
    response = api_client.get(url)
    assert response.status_code == 200


def test_customer_cannot_access_others_order(api_client, another_customer, customer_order):
    api_client.force_authenticate(user=another_customer)
    url = reverse("order-detail", args=[customer_order.id])
    response = api_client.get(url)
    assert response.status_code == 403
