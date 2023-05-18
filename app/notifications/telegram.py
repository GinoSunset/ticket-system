import logging
import requests
from notifications.models import Notification
from django.conf import settings


def create_message(notification: Notification) -> str:
    header_of_message = get_header_of_message(notification)
    return f"[{header_of_message}]\n{notification.message}"


def get_header_of_message(notification: Notification) -> str:
    if notification.subject:
        return notification.subject

    if notification.type_notify == Notification.TypeNotification.OTHER:
        return "Уведомление"

    return notification.TypeNotification(notification.type_notify).label


def send_telegram_notify_handler(notification_pk) -> bool:
    notification = Notification.objects.get(pk=notification_pk)
    if not settings.TG_BOT_NOTIFICATION_URI:
        logging.error("TG_BOT_NOTIFICATION_URI not set")
        return False

    logging.info(f"send telegram notify to {notification.user.telegram_id}")
    res = requests.post(
        settings.TG_BOT_NOTIFICATION_URI,
        json={
            "user_id": notification.user.telegram_id,
            "text": create_message(notification),
        },
    )
    if res.status_code == 200:
        return True
    return False
