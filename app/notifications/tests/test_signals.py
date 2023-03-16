import pytest

from django.core import mail
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from notifications.models import Notification


@pytest.mark.django_db
def test_send_email(
    operator_factory, notification_factory, monkeypatch_delay_send_email_on_celery
):
    operator = operator_factory()
    notify = notification_factory(user=operator, subject="Новая заявка")

    assert len(mail.outbox) == 1
    assert "Новая заявка" in mail.outbox[0].subject


@pytest.mark.django_db
@pytest.mark.parametrize(
    "type_notify, exp_subject",
    [
        ("new_ticket", "Новая заявка"),
        ("ticket_to_work", "Заявка в работе"),
        ("other", "Уведомление"),
        ("ticket_done", "Заявка выполнена"),
    ],
)
def test_email_has_needed_subject(
    operator_factory,
    notification_factory,
    ticket_factory,
    monkeypatch_delay_send_email_on_celery,
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
    monkeypatch_delay_send_email_on_celery,
):
    operator = operator_factory()
    email_contractor = "contractor@email.com"
    contractor = customer_factory(email=email_contractor)
    notify = notification_factory(user=contractor)

    assert len(mail.outbox) == 1
    assert email_contractor in mail.outbox[0].to


@pytest.mark.django_db
def test_send_email_to_customer_check_all_emails(
    notification_factory, monkeypatch_delay_send_email_on_celery, customer_factory
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
    monkeypatch_delay_send_email_on_celery, comment_factory, ticket_factory
):
    ticket = ticket_factory()
    comment = comment_factory(is_for_report=True, ticket=ticket)
    image = comment.images.create(image=SimpleUploadedFile("test.jpg", b"test"))
    comment_2 = comment_factory(is_for_report=True, ticket=ticket)
    file = comment_2.files.create(file=SimpleUploadedFile("test.txt", b"test"))

    Notification.create_notify_for_customer_when_ticket_to_done(ticket)

    assert len(mail.outbox) == 1
    assert len(mail.outbox[0].attachments) == 2
