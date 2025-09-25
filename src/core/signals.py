from django.db.models.signals import post_save
from django.dispatch import receiver
from src.orders.models import Order
from .notifications import notify_order_placed

@receiver(post_save, sender=Order)
def order_created_handler(sender, instance, created, **kwargs):
    if created:
        notify_order_placed(instance)
