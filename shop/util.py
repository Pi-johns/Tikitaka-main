from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings
from notifications.signals import notify
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_notification_to_staff(actor, verb, message, channel_name):
    channel_layer = get_channel_layer()
    staff_users = User.objects.filter(is_staff=True)
    for user in staff_users:
        notify.send(actor, recipient=user, verb=verb, description=message, level='info')
        # Send email notification
        send_mail(
            f'New {channel_name} Notification',
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        # Send WebSocket notification
        async_to_sync(channel_layer.group_send)(
            f'notifications_{user.id}',
            {
                'type': 'send_notification',
                'message': message,
            }
        )

def send_registration_notification(user):
    message = f'New user registered:\nUsername: {user.username}\nEmail: {user.email}'
    send_notification_to_staff(user, 'registered', message, 'User Registration')

def send_order_notification(order):
    message = f'Order #{order.id} completed:\nBuyer: {order.user.email}\nOrder Code: {order.order_code}'  # Adjust field names as necessary
    send_notification_to_staff(order.user, 'completed an order', message, 'Order Completion')

