import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from src.catalog.models import Category, Product
from src.orders.models import Order, OrderProducts

pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        first_name="testuser",
        last_name="user01",
        password="pass1234",
        email="test01@gmail.com",
        phone="1234567890"
    )


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def category():
    return Category.objects.create(name="Bakery")


@pytest.fixture
def product(category):
    return Product.objects.create(name="Bread", price=50, category=category)


def test_order_requires_authentication(api_client, product):
    url = reverse("order-list")
    payload = {
        "items": [
            {"product_id": product.id, "quantity": 2}
        ]
    }
    response = api_client.post(url, payload, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_order_with_items(auth_client, user, product, mocker):
    url = reverse("order-list")
    payload = {
        "items": [
            {"product_id": product.id, "quantity": 2}
        ]
    }

    mocked_notify = mocker.patch("src.orders.serializers.notify_order_placed")

    response = auth_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    data = response.data

    order = Order.objects.get(id=data["id"])
    assert order.customer == user
    assert order.total == product.price * 2
    assert order.items.count() == 1

    # fix: compare both as Decimals
    assert Decimal(data["total"]) == order.total
    assert data["items"][0]["quantity"] == 2

    mocked_notify.assert_called_once_with(order)


def test_order_item_price_is_set(auth_client, product, mocker):
    url = reverse("order-list")
    payload = {
        "items": [
            {"product_id": product.id, "quantity": 3}
        ]
    }
    mocker.patch("src.orders.serializers.notify_order_placed")

    response = auth_client.post(url, payload, format="json")
    assert response.status_code == 201

    order = Order.objects.get(id=response.data["id"])
    order_item = OrderProducts.objects.get(order=order)

    assert order_item.price == product.price
    assert order.total == Decimal(response.data["total"])
    assert order.total == product.price * 3
