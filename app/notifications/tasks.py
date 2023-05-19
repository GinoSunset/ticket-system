from ticsys import celery_app
from django.core.mail import EmailMessage
from django.template import loader
from django.conf import settings

from notifications.models import Notification
from notifications.telegram import send_telegram_notify_handler

import logging


@celery_app.task
def send_email_task(notification_pk):
    status = send_email(notification_pk)
    return status


@celery_app.task
def send_telegram_notify_task(notification_pk):
    status = send_telegram_notify_handler(notification_pk)
    return status


def send_email(notification_pk: int) -> int:
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

    email = EmailMessage(
        subject, message, settings.EMAIL_HOST_USER, notification.get_emails()
    )

    if notification.is_needed_to_attach_files():
        set_attachments(email, notification)

    if notification.bcc_email:
        email.bcc = [notification.bcc_email]
        logging.info(f"add bcc email: {notification.bcc_email} id={notification.pk}")

    if notification.cc_emails:
        email.cc = notification.cc_emails
        logging.info(f"add cc email: {email.cc } id={notification.pk}")

    status = email.send()
    return status


def set_attachments(email: EmailMessage, notification: Notification) -> None:
    if not notification.ticket:
        return
    for comment in notification.ticket.get_comments_for_report(prefetch=True):
        for file in comment.files.all():
            email.attach_file(file.file.path)
        for image in comment.images.all():
            email.attach_file(image.image.path)


def get_subject(notification: Notification) -> str:
    if notification.subject:
        return notification.subject

    if notification.type_notify == Notification.TypeNotification.OTHER:
        return "Уведомление"

    return notification.TypeNotification(notification.type_notify).label
