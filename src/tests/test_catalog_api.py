import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from src.catalog.models import Category, Product

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


def test_list_categories(api_client, category):
    url = reverse("category-list")
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data[0]["name"] == "Bakery"


def test_delete_category_with_products_fails(api_client, product):
    url = reverse("category-detail", args=[product.category.id])
    response = api_client.delete(url)
    assert response.status_code == 400
    assert "Cannot delete category" in response.data["detail"]


def test_delete_category_without_products(api_client):
    cat = Category.objects.create(name="Produce")
    url = reverse("category-detail", args=[cat.id])
    response = api_client.delete(url)
    assert response.status_code == 204


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
    # Add multiple products in category
    Product.objects.create(name="Cookie", price=100, category=category)
    Product.objects.create(name="Cake", price=200, category=category)

    url = reverse("product-average-price")
    response = api_client.get(url, {"category_id": category.id})
    assert response.status_code == 200
    assert response.data["category"] == "Bakery"
    assert response.data["average_price"] == pytest.approx(150.0)
