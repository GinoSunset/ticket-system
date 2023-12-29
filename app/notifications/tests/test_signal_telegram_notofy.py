import pytest

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from notifications.models import Notification


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
def test_telegram_notify_has_needed_text(
    operator_factory,
    notification_factory,
    ticket_factory,
    monkeypatch_delay_send_telegram_on_celery,
    mocker_bot_sender,
    type_notify,
    exp_subject,
):
    telegram_id = "164341178"
    operator = operator_factory(
        email_notify=False, telegram_notify=True, telegram_id=telegram_id
    )
    ticket = ticket_factory()
    notify = notification_factory(user=operator, type_notify=type_notify, ticket=ticket)
    assert len(mocker_bot_sender.messages) == 1
    assert exp_subject in mocker_bot_sender.messages[telegram_id]


@pytest.mark.skip
@pytest.mark.django_db
def test_send_telegram_notify_when_ticket_status_to_done(
    monkeypatch_delay_send_telegram_on_celery,
    mocker_bot_sender,
    customer_factory,
    comment_factory,
    ticket_factory,
):
    telegram_id = "164341178"
    customer = customer_factory(
        email_notify=False, telegram_notify=True, telegram_id=telegram_id
    )
    ticket = ticket_factory(customer=customer)
    comment = comment_factory(is_for_report=True, ticket=ticket)
    image = comment.images.create(image=SimpleUploadedFile("test.jpg", b"test"))
    comment_2 = comment_factory(is_for_report=True, ticket=ticket)
    file = comment_2.files.create(file=SimpleUploadedFile("test.txt", b"test"))

    Notification.create_notify_for_customer_when_ticket_to_done(ticket)

    assert len(mocker_bot_sender.messages) == 1
    assert False, "Not implemented file sending"


@pytest.mark.skip
@pytest.mark.django_db
def test_send_telegram_notify_when_ticket_status_to_cancel(
    monkeypatch_delay_send_telegram_on_celery,
    mocker_bot_sender,
    comment_factory,
    ticket_factory,
    customer_factory,
):
    telegram_id = "164341178"
    customer = customer_factory(
        email_notify=False, telegram_notify=True, telegram_id=telegram_id
    )
    ticket = ticket_factory(customer=customer)
    comment = comment_factory(is_for_report=True, ticket=ticket)
    image = comment.images.create(image=SimpleUploadedFile("test.jpg", b"test"))
    comment_2 = comment_factory(is_for_report=True, ticket=ticket)
    file = comment_2.files.create(file=SimpleUploadedFile("test.txt", b"test"))

    Notification.create_notify_for_customer_when_ticket_to_cancel(ticket)

    assert len(mocker_bot_sender.messages) == 1
    assert False, "Not implemented file sending"
