import pytest

from notifications.models import Notification
from share.models import Share
import factory
from django.db.models import signals


@pytest.mark.django_db
def test_notify_to_task_done_has_all_comment_for_report(
    ticket_factory,
    comment_factory,
    status_in_work,
    monkeypatch_delay_send_email_on_celery,
):
    ticket = ticket_factory(status=status_in_work)
    c1 = comment_factory(ticket=ticket, is_for_report=True)
    c2 = comment_factory(ticket=ticket, is_for_report=True)
    notify = Notification.create_notify_for_customer_when_ticket_to_done(ticket=ticket)
    assert notify.message is not None
    assert c1.text in notify.message
    assert c2.text in notify.message
    assert len(notify.message.split("------------")) == 3


@pytest.mark.django_db
def test_notify_to_task_cancel_has_all_comment_for_report(
    ticket_factory,
    comment_factory,
    status_in_work,
    monkeypatch_delay_send_email_on_celery,
):
    ticket = ticket_factory(status=status_in_work)
    c1 = comment_factory(ticket=ticket, is_for_report=True)
    c2 = comment_factory(ticket=ticket, is_for_report=True)
    notify = Notification.create_notify_for_customer_when_ticket_to_cancel(
        ticket=ticket
    )
    assert notify.message is not None
    assert c1.text in notify.message
    assert c2.text in notify.message
    assert len(notify.message.split("------------")) == 3


@factory.django.mute_signals(signals.post_save)
@pytest.mark.django_db
def test_create_share_link_to_contractor(
    share_factory, ticket_factory, contractor_factory
):
    contractor = contractor_factory()
    ticket = ticket_factory(contractor=contractor)
    share: Share = share_factory(ticket=ticket)
    Notification.create_notify_update_contractor(ticket=ticket)

    assert share.get_absolute_url() in Notification.objects.first().message
