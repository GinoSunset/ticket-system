from asgiref.sync import async_to_sync
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.conf import settings
from django.contrib.sites.models import Site
from channels.layers import get_channel_layer
from channels_redis.core import RedisChannelLayer

from ticket.models import Ticket
from notifications.models import Notification

from users.models import User, Customer


@receiver(post_save, sender=Ticket)
def create_notification_signal(sender, instance, created, **kwargs):
    if created:
        create_notifications(instance)


@receiver(post_save, sender=Ticket)
def send_ticket_to_channel(sender, instance, created, **kwargs):
    if created:
        channel_layer: RedisChannelLayer = get_channel_layer()
        send_ticket_to_operators(instance, channel_layer)
        send_ticket_to_customer(instance, channel_layer)
        send_ticket_to_contractor(instance, channel_layer)
        async_to_sync(channel_layer.close_pools)()


def send_ticket_to_operators(instance, channel_layer):
    async_to_sync(channel_layer.group_send)(
        "operators",
        {"type": "send_info_to_user_group", "ticket_id": instance.id},
    )


def send_ticket_to_customer(instance, channel_layer):
    if instance.customer:
        customer: Customer = instance.customer.get_role_user()
        async_to_sync(channel_layer.group_send)(
            f"customer_{customer.pk}",
            {"type": "send_info_to_user_group", "ticket_id": instance.id},
        )


def send_ticket_to_contractor(instance, channel_layer):
    if instance.contractor:
        async_to_sync(channel_layer.group_send)(
            f"contractor_{instance.contractor.pk}",
            {"type": "send_info_to_user_group", "ticket_id": instance.id},
        )


def create_notifications(instance: Ticket):
    """
    create notifications for new ticket
    all users with role "operator" and "admin" will get notification
    """
    users = get_users_for_create_notify(instance)

    link = f"{settings.PROTOCOL}://{Site.objects.get_current()}{instance.get_absolute_url()}"
    message = (
        f"Создана заявка #{instance.pk}. Заказчик: {instance.customer}. Ссылка: {link}"
    )
    for user in users:
        Notification.objects.create(
            user=user,
            message=message,
            type_notify=Notification.TypeNotification.NEW_TICKET,
        )


def get_users_for_create_notify(instance):
    customer: Customer = instance.customer.get_role_user()
    operators = None
    if customer.is_customer:
        operators = customer.get_operators()
        operator_user = User.objects.filter(id__in=operators)
    admins = User.objects.filter(is_staff=True)
    users = operator_user | admins

    return users.distinct()
