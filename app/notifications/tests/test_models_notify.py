import pytest

from notifications.models import Notification


@pytest.mark.django_db
def test_notify_to_task_done_has_all_comment_for_report(
    ticket_factory, comment_factory, status_in_work
):
    ticket = ticket_factory(status=status_in_work)
    c1 = comment_factory(ticket=ticket, is_for_report=True)
    c2 = comment_factory(ticket=ticket, is_for_report=True)
    notify = Notification.create_notify_for_customer_when_ticket_to_done(ticket=ticket)
    assert notify.message is not None
    assert c1.text in notify.message
    assert c2.text in notify.message
    assert len(notify.message.split("------------")) == 3
