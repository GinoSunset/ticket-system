from django.conf import settings
from imap_tools import MailBox, AND
from imap_tools.message import MailMessage
import logging

from users.models import Customer, User
from additionally.models import Dictionary
from .models import Ticket
from .parsers import BaseParser


def save_tickets_from_emails() -> int:
    emails = get_new_emails()
    count = 0
    for email in emails:
        if settings.SUBJECT_TO_TICKET not in email.subject.lower():
            continue
        logging.info(f"Processing ticket from {email.from_}")
        status = create_ticket_from_email(email)
        if status:
            count += 1
    return count


def get_new_emails():
    with MailBox(host=settings.EMAIL_IMAP_HOST, port=settings.EMAIL_IMAP_PORT).login(
        username=settings.EMAIL_HOST_USER, password=settings.EMAIL_HOST_PASSWORD
    ) as mailbox:
        for mail in mailbox.fetch(AND(seen=False), charset="utf8"):
            yield mail


def create_ticket_from_email(email: MailMessage) -> bool:
    email_customer = email.from_
    message = email.text or email.html

    try:
        customer = Customer.objects.get(email=email_customer)
    except Customer.DoesNotExist:
        logging.info(f"Customer with email {email_customer} not found")
        return False
    ticket_info = get_info_from_message(message, customer)
    creator = User.objects.get(username=settings.TICKET_CREATOR_USERNAME)
    status = Dictionary.get_status_ticket("work")
    Ticket.objects.create(
        customer=customer, creator=creator, status=status, **ticket_info
    )
    return True


def get_info_from_message(message: str, customer: Customer) -> dict:
    parser_name = customer.get_parser()
    parser = BaseParser.get_parser(parser_name)
    try:
        info = parser.parse(message)
    except Exception as e:
        logging.error(f"Error parsing with: {type(e)} {str(e)}. Try default parser")
        return BaseParser().parse(message)
    return info
