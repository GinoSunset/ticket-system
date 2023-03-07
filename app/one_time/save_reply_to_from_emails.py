"""
script to save all cc from emails in ticket._reply_to_emails
"""
from imap_tools import MailBox
import os
import sys
import django
import logging


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ticsys.settings")
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
django.setup()


from django.conf import settings
from ticket.models import Ticket

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
# add logging save to file
fh = logging.FileHandler("save_reply_to_from_emails.log")
fh.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logging.getLogger().addHandler(fh)


def get_mails():
    with MailBox(host=settings.EMAIL_IMAP_HOST, port=settings.EMAIL_IMAP_PORT).login(
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        initial_folder=settings.EMAIL_INITIAL_FOLDER,
    ) as mailbox:
        for mail in mailbox.fetch(charset="utf8"):
            yield mail


def load_reply_to():
    for email in get_mails():
        logging.info(f"Processing email {email.subject}")
        id_email_message = email.headers.get("message-id")[0].strip()
        ticket = get_ticket(id_email_message)
        if ticket:
            emails_to_reply = email.cc
            ticket._reply_to_emails = ",".join(emails_to_reply)
            ticket.save()
            logging.info(
                f"Ticket {ticket.id} updated with reply_to {ticket._reply_to_emails}"
            )


def get_ticket(id_email_message):

    tickets = Ticket.objects.filter(id_email_message=id_email_message)
    if not tickets:
        logging.info(f"Ticket with id_email_message {id_email_message} not found")
        return None
    if len(tickets) > 1:
        logging.info(f"More than one ticket with id_email_message {id_email_message}")
    return tickets.first()


if __name__ == "__main__":
    logging.info("Starting script")
    load_reply_to()
