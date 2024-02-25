import pytest
from django.conf import settings
from django.db.models import signals
from imap_tools.message import MailMessage
from ticket.handlers import (
    create_ticket_from_email,
    create_comment_from_email,
    cleanup_comment_text,
    processing_email,
)
from ticket.models import Ticket
import factory

from users.models import CustomerProfile
from notifications.models import Notification


@pytest.mark.django_db
def test_creating_ticket_form_emails(email_ticket, customer_factory, redis):
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
    email_ticket, customer_factory, redis
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
    redis,
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
def test_create_comment_from_email(
    email_ticket, customer_factory, ticket_factory, redis
):
    customer_factory(email=email_ticket.from_)
    ticket: Ticket = ticket_factory(id_email_message="<asdfasdfasdf@vim.ru>")
    st = create_comment_from_email(email_ticket)
    assert st
    assert ticket.comments.count() == 1


def test_cleanup_comment(text_reply):
    assert cleanup_comment_text(text_reply) == "Вот так"


@pytest.mark.django_db
def test_create_ticket(monkeypatch, email_with_img, customer_factory):
    from ticket.handlers import save_tickets_from_emails

    customer_factory(email=email_with_img.from_)

    def mock_get_new_emails():
        return [email_with_img]

    monkeypatch.setattr("ticket.handlers.get_new_emails", mock_get_new_emails)
    assert save_tickets_from_emails()


@pytest.mark.skip
@pytest.mark.django_db
def test_load_ticket(customer_factory):
    from ticket.handlers import save_tickets_from_emails

    user = customer_factory(email="gino-sunset@yandex.ru")
    user.profile.parser = "DMV2"
    user.profile.save()

    result = save_tickets_from_emails()
    assert result == 1


@pytest.mark.django_db
def test_creating_comment_from_emails_with_trees(
    customer_factory, ticket_factory, redis
):
    sap_id_from_email = "8001128295"
    with open(
        settings.BASE_DIR / f"ticket/tests/RE_{sap_id_from_email}_tets.eml", "rb"
    ) as f:
        data = f.read()
    email_ticket = MailMessage.from_bytes(data)

    customer_factory(email=email_ticket.from_)
    ticket: Ticket = ticket_factory(sap_id=sap_id_from_email)
    status = processing_email(email_ticket)

    assert status


@pytest.mark.django_db
def test_create_comment_with_img_from_email(
    email_with_img, customer_factory, ticket_factory, redis
):
    customer = customer_factory(email=email_with_img.from_)
    customer.refresh_from_db()
    customer.profile.parser = "DM"
    customer.profile.save()
    create_ticket_from_email(email_with_img)
    assert Ticket.objects.all().count() > 0
    ticket = Ticket.objects.first()
    assert ticket.comments.count() == 1


@pytest.mark.django_db
def test_proceeding_html_text(customer_factory, redis):
    with open(settings.BASE_DIR / "ticket/tests/dmv2.eml", "rb") as f:
        data = f.read()
    mail = MailMessage.from_bytes(data)
    customer = customer_factory(email=mail.from_)
    customer.refresh_from_db()
    customer.profile.parser = "DMV2"
    customer.profile.save()
    create_ticket_from_email(email=mail)
    ticket = Ticket.objects.all().get()
    assert ticket.sap_id
    assert ticket.address


@pytest.mark.django_db
@factory.django.mute_signals(signals.post_save)
def test_create_email_as_comment_if_sap_exists(
    customer_factory,
    ticket_factory,
    email_ticket,
    status_done,
    status_new,
    operator_factory,
):
    sap_id = "800111258011"
    operator = operator_factory()
    email_ticket.headers.pop("in-reply-to")
    customer = customer_factory(email=email_ticket.from_)
    CustomerProfile.objects.create(user=customer)
    customer.profile.parser = "DM"
    customer.profile.save()
    operator.customers.add(customer.profile)
    ticket = ticket_factory(sap_id=sap_id, customer=customer, status=status_done)
    processing_email(email_ticket)
    ticket.refresh_from_db()
    assert ticket.comments.count() == 1
    assert ticket.comments.first().text
    assert ticket.comments.first().author == customer
    assert ticket.comments.first().author.email == email_ticket.from_
    assert ticket.status == status_new

    notify = Notification.objects.first()
    assert notify.message


@pytest.mark.django_db
@factory.django.mute_signals(signals.post_save)
def test_create_ticket_from_email_dmv2_serv(email_dmv2_serv, customer_factory):
    customer = customer_factory(email=email_dmv2_serv.from_)
    CustomerProfile.objects.create(user=customer)

    customer.profile.parser = "DMV2"
    customer.profile.save()
    status = create_ticket_from_email(email=email_dmv2_serv)
    assert status
    ticket = Ticket.objects.all().get()
    assert ticket.sap_id
    assert ticket.address
    assert ticket.status.code == "new"


@pytest.mark.django_db
@factory.django.mute_signals(signals.post_save)
def test_from_dmv2_get_emails_for_reply(email_dmv2_serv, customer_factory):
    """
    Взять почту из сообщения: "Вы можете связаться с заказчиком по адресу annfedorova@detmir.ru"
    """
    customer = customer_factory(email=email_dmv2_serv.from_)
    CustomerProfile.objects.create(user=customer)

    customer.profile.parser = "DMV2"
    customer.profile.save()
    status = create_ticket_from_email(email=email_dmv2_serv)
    assert status
    ticket = Ticket.objects.all().get()
    assert "1212@fl.com" in ticket.reply_to_emails


def get_email_from_html():
    """return 1212@fl.com from text"""
    import re

    text = 'Цветные рамки\r\nРамки сами по себе переодически начинают краснеть, иногда перестают работать\r\n\r\n<a href="http://sapepp.ЕК.ru:50000/irj/21212">Для выполнения инцидента перейдите по ссылке.</a>\r\n\r\nВы можете связаться с заказчиком по  адресу <a href="mailto:1212@fl.com">1212@fl.com</a>'

    email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    # This regex pattern matches email addresses

    match = re.search(email_regex, text)
    if match:
        email = match.group()
        print(email)
    else:
        print("No email address found")
