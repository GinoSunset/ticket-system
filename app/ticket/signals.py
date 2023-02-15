from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.conf import settings
from django.contrib.sites.models import Site

from ticket.models import Ticket
from notifications.models import Notification

from users.models import User, Customer


@receiver(post_save, sender=Ticket)
def create_notification_signal(sender, instance, created, **kwargs):
    return
    if created:
        create_notifications(instance)


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
