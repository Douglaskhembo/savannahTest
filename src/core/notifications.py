from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from .africatalking import africastalking_client

User = get_user_model()


def notify_order_placed(order):
    # --- SMS to customer ---
    phone = order.customer.phone
    if phone and phone.startswith("0"):  # normalize Kenyan numbers
        phone = "+254" + phone[1:]

    msg = f"Hi {order.customer.first_name}, your order #{order.order_code} has been placed. Total: {order.total}"
    try:
        africastalking_client.send_sms([phone], msg)
    except Exception as e:
        print("SMS failed:", e)

    admin_emails = list(
        User.objects.filter(role=User.Role.ADMIN, is_active=True)
        .exclude(email__isnull=True)
        .exclude(email__exact="")
        .values_list("email", flat=True)
    )

    if admin_emails:
        subject = f"Purchase order {order.order_code} placed"
        body = (
            f"New order has been placed, below are order details Code\n"
            f"Order Code: {order.order_code}\n"
            f"Customer name: {order.customer.first_name} {order.customer.last_name} \n"
            f"Customer email: ({order.customer.email})\n"
            f"Total: {order.total}\n\n"
            "Items:\n"
        )
        for it in order.items.all():
            body += f" - {it.product.name} x {it.quantity} @ {it.price}\n"

        email = EmailMessage(subject, body, to=admin_emails)
        try:
            email.send()
        except Exception as e:
            print("Email failed:", e)
