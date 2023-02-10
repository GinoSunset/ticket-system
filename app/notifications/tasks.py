from ticsys import celery_app
from django.core.mail import send_mail
from django.template import loader
from django.conf import settings

from notifications.models import Notification


@celery_app.task
def send_email_task(notification_pk):
    notification = Notification.objects.get(pk=notification_pk)

    message = loader.get_template("notifications/mail_create_new_ticket.txt").render(
        {"message": notification.message}
    )
    subject = "Новая заявка"
    status = send_mail(
        subject, message, settings.EMAIL_HOST_USER, [notification.user.email]
    )

    return status
