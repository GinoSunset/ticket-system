import pytest
from ticket.handlers import create_ticket_from_email
from ticket.models import Ticket


@pytest.mark.django_db
def test_creating_ticket_form_emails(email_ticket, customer_factory):
    customer_factory(email=email_ticket.from_)
    create_ticket_from_email(email_ticket)
    assert Ticket.objects.all().count() > 0
    ticket = Ticket.objects.first()
    assert ticket.creator.username == "email_robot"
    assert ticket.customer.email == email_ticket.from_
    assert ticket.description == email_ticket.text
    assert ticket.status.code == "work"
