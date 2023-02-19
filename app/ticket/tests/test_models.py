import pytest
from additionally.models import Dictionary


@pytest.mark.django_db
def test_save_completion_date_if_status_done(ticket_factory):
    ticket = ticket_factory()
    assert ticket.completion_date is None

    ticket.status = Dictionary.objects.get(code="done")
    ticket.save()
    ticket.refresh_from_db()
    assert ticket.completion_date is not None


@pytest.mark.django_db
def test_save_completion_date_if_status_done_and_completion_date_is_set(
    ticket_factory,
):
    ticket = ticket_factory()
    assert ticket.completion_date is None
    ticket.status = Dictionary.objects.get(code="done")
    ticket.save()
    ticket.refresh_from_db()
    assert ticket.completion_date is not None
