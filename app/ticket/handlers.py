import re

from django.conf import settings
from django.core.files.base import ContentFile

from imap_tools import MailBox, AND
from imap_tools.message import MailMessage
import logging

from users.models import Customer, User
from additionally.models import Dictionary
from .models import Ticket, Comment
from .parsers import BaseParser
from .utils import is_image


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
    comment = ticket.comments.create(
        text=message,
        author=user,
        id_email_message=id_email_message,
    )
    save_attachment(email, ticket, user, comment)
    return True


def get_ticket_by_message_id_reply(id_email_message_in_reply_to):
    comment = Comment.objects.filter(
        id_email_message=id_email_message_in_reply_to
    ).last()
    if comment:
        return comment.ticket
    ticket = Ticket.objects.filter(id_email_message=id_email_message_in_reply_to).last()
    if not ticket:
        raise Ticket.DoesNotExist
    return ticket


def get_new_emails():
    with MailBox(host=settings.EMAIL_IMAP_HOST, port=settings.EMAIL_IMAP_PORT).login(
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        initial_folder=settings.EMAIL_INITIAL_FOLDER,
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
    message = remove_duplicate_new_lines(message)
    id_email_message = email.headers.get("message-id")[0].strip()
    ticket_info = get_info_from_message(message, customer)
    creator = User.objects.get(username=settings.TICKET_CREATOR_USERNAME)
    status = Dictionary.get_status_ticket("new")
    type_ticket = Dictionary.get_type_ticket(Ticket.default_type_code)

    ticket = Ticket.objects.create(
        customer=customer,
        creator=creator,
        status=status,
        type_ticket=type_ticket,
        id_email_message=id_email_message,
        **ticket_info,
    )
    save_attachment(email, ticket, customer)
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
    return remove_duplicate_new_lines("\n".join(new_lines).strip())


def remove_duplicate_new_lines(text: str) -> str:
    text = re.sub(r"$\n{3,}", "\n\n", text)
    text = re.sub(r"$(\r\n){3,}", "\r\n\r\n", text)
    return text


def save_attachment(email: MailBox, ticket: Ticket, user, comment: Comment = None):
    if not email.attachments:
        return
    if not comment:
        comment = ticket.comments.create(author=user, text="Вложение из письма")
    for file in email.attachments:
        file_obj = ContentFile(content=file.payload, name=file.filename)
        if is_image(file=file_obj):
            comment.images.create(image=file_obj)
            logging.info(f"Saving image {file.filename} from {email.from_}")
            continue
        comment.files.create(file=file_obj)
        logging.info(f"Saving file {file.filename} from {email.from_} ")
