from ticsys import celery_app
from django.core.mail import send_mail
from django.template import loader
from django.conf import settings

from notifications.models import Notification


@celery_app.task
def send_email_task(notification_pk):
    status = send_email(notification_pk)
    return status


def send_email(notification_pk):
    type_mail_template = {
        "create_new_ticket": "notifications/mail/create_new_ticket.txt",
        "ticket_to_work": "notifications/mail/ticket_to_work.txt",
        "other": "notifications/mail/other.txt",
    }

    notification = Notification.objects.get(pk=notification_pk)
    template = type_mail_template.get(
        notification.type_notify, "notifications/mail/other.txt"
    )
    message = loader.get_template(template).render({"message": notification.message})
    subject = get_subject(notification)
    status = send_mail(
        subject, message, settings.EMAIL_HOST_USER, notification.get_emails()
    )

    return status


def get_subject(notification):
    if notification.subject:
        return notification.subject

    if notification.type_notify == Notification.TypeNotification.OTHER:
        return "Уведомление"

    return notification.TypeNotification(notification.type_notify).label
