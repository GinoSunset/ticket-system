from typing import Callable, Literal
import pytest

from django.core import mail
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from notifications.models import Notification


@pytest.mark.django_db
def test_send_email(
    operator_factory, notification_factory, monkeypatch_delay_send_email_on_celery: None
):
    operator = operator_factory()
    notify = notification_factory(user=operator, subject="Новая заявка")

    assert len(mail.outbox) == 1
    assert "Новая заявка" in mail.outbox[0].subject


@pytest.mark.django_db
def test_send_telegram(
    operator_factory,
    notification_factory,
    monkeypatch_delay_send_telegram_on_celery: None,
    mocker_bot_sender,
):
    telegram_id = "164341178"
    operator = operator_factory(
        email_notify=False, telegram_notify=True, telegram_id=telegram_id
    )
    notify: Notification = notification_factory(
        user=operator, subject="Новая заявка", message="test"
    )

    assert len(mocker_bot_sender.messages) == 1
    assert "Новая заявка" in mocker_bot_sender.messages[telegram_id]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "type_notify, exp_subject",
    [
        ("new_ticket", "Новая заявка"),
        ("ticket_to_work", "Заявка в работе"),
        ("other", "Уведомление"),
        ("ticket_done", "Заявка выполнена"),
        ("ticket_cancel", "Заявка отменена"),
    ],
)
def test_email_has_needed_subject(
    operator_factory,
    notification_factory,
    ticket_factory,
    monkeypatch_delay_send_email_on_celery: None,
    type_notify,
    exp_subject,
):
    operator = operator_factory()
    ticket = ticket_factory()
    notify = notification_factory(user=operator, type_notify=type_notify, ticket=ticket)
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == exp_subject


@pytest.mark.django_db
def test_send_email_to_contractor_if_him_set(
    customer_factory,
    operator_factory,
    notification_factory,
    monkeypatch_delay_send_email_on_celery: None,
):
    operator = operator_factory()
    email_contractor = "contractor@email.com"
    contractor = customer_factory(email=email_contractor)
    notify = notification_factory(user=contractor)

    assert len(mail.outbox) == 1
    assert email_contractor in mail.outbox[0].to


@pytest.mark.django_db
def test_send_email_to_customer_check_all_emails(
    notification_factory, monkeypatch_delay_send_email_on_celery: None, customer_factory
):
    emails = ["example1@email.com", "example2@email.com", settings.EMAIL_HOST_USER]
    emails_str = ",".join(emails)
    user = customer_factory()

    notify = notification_factory(emails=emails_str, user=user)
    assert len(mail.outbox) == 1
    expected_emails = set(emails)
    expected_emails.add(user.email)
    expected_emails.remove(settings.EMAIL_HOST_USER)
    assert expected_emails == set(mail.outbox[0].to)


@pytest.mark.django_db
def test_send_email_when_ticket_status_to_done(
    monkeypatch_delay_send_email_on_celery: None, comment_factory, ticket_factory
):
    ticket = ticket_factory()
    comment = comment_factory(is_for_report=True, ticket=ticket)
    image = comment.images.create(image=SimpleUploadedFile("test.jpg", b"test"))
    comment_2 = comment_factory(is_for_report=True, ticket=ticket)
    file = comment_2.files.create(file=SimpleUploadedFile("test.txt", b"test"))

    Notification.create_notify_for_customer_when_ticket_to_done(ticket)

    assert len(mail.outbox) == 1
    assert len(mail.outbox[0].attachments) == 2


@pytest.mark.django_db
def test_send_email_when_ticket_status_to_cancel(
    monkeypatch_delay_send_email_on_celery: None, comment_factory, ticket_factory
):
    ticket = ticket_factory()
    comment = comment_factory(is_for_report=True, ticket=ticket)
    image = comment.images.create(image=SimpleUploadedFile("test.jpg", b"test"))
    comment_2 = comment_factory(is_for_report=True, ticket=ticket)
    file = comment_2.files.create(file=SimpleUploadedFile("test.txt", b"test"))

    Notification.create_notify_for_customer_when_ticket_to_cancel(ticket)

    assert len(mail.outbox) == 1
    assert len(mail.outbox[0].attachments) == 2


@pytest.mark.django_db
@pytest.mark.parametrize(
    "func",
    [
        Notification.create_notify_for_customer_when_ticket_to_cancel,
        Notification.create_notify_for_customer_when_ticket_to_done,
        Notification.create_notify_for_customer_when_ticket_to_work,
    ],
)
def test_notify_change_status_has_bcc_email_manager(
    monkeypatch_delay_send_email_on_celery: None, ticket_factory, func
):
    ticket = ticket_factory()
    func(ticket)
    assert settings.MANAGER_EMAIL in mail.outbox[0].bcc
