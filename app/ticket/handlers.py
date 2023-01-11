from django.conf import settings
from imap_tools import MailBox, AND
from imap_tools.message import MailMessage
import logging

from .models import Ticket


def save_tickets_from_emails():
    emails = get_new_emails()
    for email in emails:
        logging.info(f"save email from {email.from_}")
        create_ticket_from_email(email)


def get_new_emails():
    with MailBox(host=settings.EMAIL_IMAP_HOST, port=settings.EMAIL_IMAP_PORT).login(
        username=settings.EMAIL_HOST_USER, password=settings.EMAIL_HOST_PASSWORD
    ) as mailbox:
        for mail in mailbox.fetch(AND(to=settings.EMAIL_TO_TICKET)):
            yield mail


def create_ticket_from_email(email: MailMessage):
    email_customer = email.from_
    message = email.text
    Ticket.objects.create(description=message)
