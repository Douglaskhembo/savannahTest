from django.conf import settings
from django.core.mail import EmailMessage
from .africatalking import africastalking_client

def notify_order_placed(order):
    # send SMS to customer
    phone = order.customer.phone
    msg = f"Hi {order.customer.username}, your order #{order.id} has been placed. Total: {order.total}"
    try:
        africastalking_client.send_sms([phone], msg)
    except Exception as e:
        print('SMS failed', e)

    # send email to admin
    subject = f"New order #{order.id} placed"
    body = f"Order ID: {order.id}\nCustomer: {order.customer}\nTotal: {order.total}\nItems:\n"
    for it in order.items.all():
        body += f" - {it.product.name} x {it.quantity} @ {it.price}\n"
    email = EmailMessage(subject, body, to=[settings.ADMIN_EMAIL])
    try:
        email.send()
    except Exception as e:
        print('Email failed', e)