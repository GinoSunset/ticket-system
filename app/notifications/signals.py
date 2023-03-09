from django.dispatch import receiver
from django.db.models.signals import post_save
from django.template import loader

from notifications.models import Notification
from notifications.tasks import send_email_task


@receiver(post_save, sender=Notification)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        send_notify(instance)


def send_notify(notification):
    if notification.user.telegram_id and notification.user.telegram_notify:
        send_telegram_notify(notification.user, notification)
    if notification.user.email_notify and (
        notification.emails or notification.email or notification.user.email
    ):
        send_email_task.delay(notification.pk)


def send_telegram_notify(user, notification):
    message = loader.get_template("notifications/mail_create_new_ticket.txt").render({})
    # send telegram message (not implemented)
