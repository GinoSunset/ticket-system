from django.core import mail

import pytest


@pytest.mark.django_db
def test_send_email(
    operator_factory, notification_factory, monkeypatch_delay_send_email_on_celery
):
    operator = operator_factory()
    notify = notification_factory(user=operator)

    assert len(mail.outbox) == 1
    assert "Новая заявка" in mail.outbox[0].subject


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
