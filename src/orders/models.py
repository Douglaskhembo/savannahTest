from django.db import models
from django.conf import settings
from src.catalog.models import Product

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELED = "CANCELED", "Canceled"
        RETURNED = "RETURNED", "Returned"

    order_code = models.CharField(max_length=100, unique=True)
    status = models.BooleanField(default=Status.PENDING)
    created = models.DateTimeField(auto_now_add=True)
    quantity = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')

    def __str__(self):
        return f"Order {self.id} by {self.customer}"

class OrderProducts(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} by {self.product.name}"
