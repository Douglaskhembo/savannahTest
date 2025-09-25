from django.db import models
from django.utils import timezone

class Category(models.Model):
    category_code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        unique_together = ('name', 'parent')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.category_code:
            today_str = timezone.now().strftime("%Y%m%d")
            prefix = f"CAT-{today_str}-"

            last = Category.objects.filter(category_code__startswith=prefix).order_by("-category_code").first()
            if last:
                last_number = int(last.category_code.split("-")[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.category_code = f"{prefix}{new_number:04d}"

        super().save(*args, **kwargs)

    def get_descendants(self):
        descendants = []
        children = self.children.all()
        for child in children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants


class Product(models.Model):
    product_code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.product_code:
            today_str = timezone.now().strftime("%Y%m%d")
            prefix = f"PROD-{today_str}-"

            last = Product.objects.filter(product_code__startswith=prefix).order_by("-product_code").first()
            if last:
                last_number = int(last.product_code.split("-")[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.product_code = f"{prefix}{new_number:04d}"

        super().save(*args, **kwargs)
