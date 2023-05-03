import pytest
from additionally.models import Dictionary
from share.models import Share


@pytest.mark.django_db
def test_create_share_after_ticket_to_work(ticket_factory):
    status = Dictionary.get_status_ticket("new")
    status_work = Dictionary.get_status_ticket("work")
    ticket = ticket_factory(status=status)
    assert not Share.objects.filter(ticket=ticket).exists()
    ticket.status = status_work
    ticket.save()
    ticket.refresh_from_db()
    assert ticket.share


@pytest.mark.django_db
def test_remove_share_after_close_ticket():
    assert False


@pytest.mark.django_db
def test_remove_share_after_done_ticket():
    assert False
