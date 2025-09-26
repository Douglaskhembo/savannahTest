from django.db import models
from django.utils import timezone
from django.conf import settings
from src.catalog.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELED = "CANCELED", "Canceled"
        RETURNED = "RETURNED", "Returned"

    order_code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    total = models.DecimalField(decimal_places=2, max_digits=10, default=0)

    def __str__(self):
        return f"{self.order_code} by {self.customer}"

    def save(self, *args, **kwargs):
        if not self.order_code:
            today_str = timezone.now().strftime("%Y%m%d")
            prefix = f"ORD-{today_str}-"

            last = Order.objects.filter(order_code__startswith=prefix).order_by("-order_code").first()
            if last:
                last_number = int(last.order_code.split("-")[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.order_code = f"{prefix}{new_number:04d}"

        super().save(*args, **kwargs)


class OrderProducts(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    price = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.order.order_code}"
