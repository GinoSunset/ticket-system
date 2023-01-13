from django.conf import settings
from imap_tools import MailBox, AND
from imap_tools.message import MailMessage
import logging

from users.models import Customer, User
from additionally.models import Dictionary
from .models import Ticket


def save_tickets_from_emails() -> int:
    emails = get_new_emails()
    count = 0
    for email in emails:
        logging.info(f"Processing ticket from {email.from_}")
        status = create_ticket_from_email(email)
        if status:
            count += 1
    return count


def get_new_emails():
    with MailBox(host=settings.EMAIL_IMAP_HOST, port=settings.EMAIL_IMAP_PORT).login(
        username=settings.EMAIL_HOST_USER, password=settings.EMAIL_HOST_PASSWORD
    ) as mailbox:
        for mail in mailbox.fetch(
            AND(subject=settings.SUBJECT_TO_TICKET, seen=False), charset="utf8"
        ):
            yield mail


def create_ticket_from_email(email: MailMessage) -> bool:
    email_customer = email.from_
    message = email.text

    try:
        customer = Customer.objects.get(email=email_customer)
    except Customer.DoesNotExist:
        logging.info(
            f"Customer with email {email_customer} not found. Ticket not created"
        )
        return False

    creator = User.objects.get(username=settings.TICKET_CREATOR_USERNAME)
    status = Dictionary.get_status_ticket("work")
    Ticket.objects.create(
        customer=customer, description=message, creator=creator, status=status
    )
    return True
