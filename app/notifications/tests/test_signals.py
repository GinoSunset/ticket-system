from django.core import mail

import pytest


@pytest.mark.django_db
def test_send_email(operator_factory, notification_factory):
    operator = operator_factory()
    notify = notification_factory(user=operator)

    assert len(mail.outbox) == 1
    assert "Новая заявка" in mail.outbox[0].subject
