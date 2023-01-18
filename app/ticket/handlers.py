from django.conf import settings
from imap_tools import MailBox, AND
from imap_tools.message import MailMessage
import logging

from users.models import Customer, User
from additionally.models import Dictionary
from .models import Ticket, Comment
from .parsers import BaseParser


def save_tickets_from_emails() -> int:
    emails = get_new_emails()
    count = 0
    for email in emails:
        if not is_email_for_processing(email):
            logging.info(
                f"Email with subject {email.subject} is not for processing. Skip"
            )
            continue
        logging.info(f"Processing ticket from {email.from_}")
        if is_reply_message(email):
            logging.info("Email is reply message. Save as comment")
            status = create_comment_from_email(email)
        else:
            status = create_ticket_from_email(email)
        if status:
            count += 1
    return count


def is_email_for_processing(email: MailMessage) -> bool:
    if settings.SUBJECT_TO_TICKET not in email.subject.lower():
        return False
    user_email = email.from_
    is_user_exist = User.objects.filter(email__iregex=user_email).exists()
    if not is_user_exist:
        logging.info(f"User with email {user_email} not found")
        return False
    return True


def is_reply_message(email: MailMessage) -> bool:
    if email.headers.get("in-reply-to"):
        return True
    return False


def create_comment_from_email(email: MailMessage) -> bool:
    email_customer = email.from_
    user = User.objects.get(email__iregex=email_customer)

    message = email.text or email.html
    id_email_message = email.headers.get("message-id")[0].strip()
    id_email_message_in_reply_to = email.headers.get("in-reply-to")[0]
    try:
        ticket = get_ticket_by_message_id_reply(id_email_message_in_reply_to)
    except Ticket.DoesNotExist:
        logging.info(
            f"Ticket with id_email_message {id_email_message_in_reply_to} not found"
        )
        return False
    message = cleanup_comment_text(message)
    ticket.comments.create(
        text=message,
        author=user,
        id_email_message=id_email_message,
    )
    return True


def get_ticket_by_message_id_reply(id_email_message_in_reply_to):
    try:
        comment = Comment.objects.get(id_email_message=id_email_message_in_reply_to)
    except Comment.DoesNotExist:
        return Ticket.objects.get(id_email_message=id_email_message_in_reply_to)
    return comment.ticket


def get_new_emails():
    with MailBox(host=settings.EMAIL_IMAP_HOST, port=settings.EMAIL_IMAP_PORT).login(
        username=settings.EMAIL_HOST_USER, password=settings.EMAIL_HOST_PASSWORD
    ) as mailbox:
        for mail in mailbox.fetch(AND(seen=False), charset="utf8"):
            yield mail


def create_ticket_from_email(email: MailMessage) -> bool:
    email_customer = email.from_
    user = User.objects.get(email__iregex=email_customer)
    if not user.is_customer:
        logging.info(f"User {user} is not customer and can't create ticket from email")
        return False
    customer = user.get_role_user()
    message = email.text or email.html
    id_email_message = email.headers.get("message-id")[0].strip()
    ticket_info = get_info_from_message(message, customer)
    creator = User.objects.get(username=settings.TICKET_CREATOR_USERNAME)
    status = Dictionary.get_status_ticket("work")
    Ticket.objects.create(
        customer=customer,
        creator=creator,
        status=status,
        id_email_message=id_email_message,
        **ticket_info,
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


def cleanup_comment_text(text: str) -> str:
    """
    remove all text start char '>' and text after it
    """
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith(">"):
            continue
        new_lines.append(line)
    return "\n".join(new_lines).strip()
