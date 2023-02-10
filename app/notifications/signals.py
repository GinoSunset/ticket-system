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
    if notification.user:
        if notification.user.email and notification.user.email_notify:
            send_email_task.delay(notification.pk)
        if notification.user.telegram_id and notification.user.telegram_notify:
            send_telegram_notify(notification.user, notification)


def send_telegram_notify(user, notification):
    message = loader.get_template("notifications/mail_create_new_ticket.txt").render({})
    # send telegram message (not implemented)
