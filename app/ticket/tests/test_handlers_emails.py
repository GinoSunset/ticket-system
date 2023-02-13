import pytest
from ticket.handlers import (
    create_ticket_from_email,
    create_comment_from_email,
    cleanup_comment_text,
)
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
    assert ticket.status.code == "new"


@pytest.mark.django_db
def test_creating_ticket_form_emails_has_default_type_hardware_setup(
    email_ticket, customer_factory
):
    customer_factory(email=email_ticket.from_)
    create_ticket_from_email(email_ticket)
    ticket = Ticket.objects.first()
    assert ticket.type_ticket.code == "hardware_setup"


@pytest.mark.django_db
def test_create_DM_ticket(
    email_ticket,
    marked_up_text_DM_ticket,
    customer_factory,
    shop_address,
    sap_number,
):
    descriptor, _, added_descriptor, _ = marked_up_text_DM_ticket

    user = customer_factory(email=email_ticket.from_)
    user.profile.parser = "DM"
    user.profile.save()

    create_ticket_from_email(email_ticket)

    ticket = Ticket.objects.first()
    assert (
        ticket.description.splitlines()
        == (descriptor + added_descriptor).strip().splitlines()
    )

    assert ticket.address == shop_address

    assert ticket.sap_id == sap_number


@pytest.mark.django_db
def test_create_comment_from_email(email_ticket, customer_factory, ticket_factory):
    customer_factory(email=email_ticket.from_)
    ticket: Ticket = ticket_factory(id_email_message="<asdfasdfasdf@vim.ru>")
    st = create_comment_from_email(email_ticket)
    assert st
    assert ticket.comments.count() == 1


def test_cleanup_comment(text_reply):

    assert cleanup_comment_text(text_reply) == "Вот так"


@pytest.mark.skip
@pytest.mark.django_db
def test_load_ticket(customer_factory):
    from ticket.handlers import save_tickets_from_emails

    user = customer_factory(email="gino-sunset@yandex.ru")
    user.profile.parser = "DM"
    user.profile.save()

    result = save_tickets_from_emails()
    assert result == 1
