import pytest
from ticket.handlers import create_ticket_from_email, get_new_emails
from ticket.models import Ticket


@pytest.mark.django_db
def test_creating_ticket_form_emails(email_ticket):
    create_ticket_from_email(email_ticket)
    assert Ticket.objects.all().count() > 0
    assert False


@pytest.mark.django_db
def test_failed():
    """"""
    mails = get_new_emails()
    for i in mails:
        print(i.to)
    assert False