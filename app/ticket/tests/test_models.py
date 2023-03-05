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


@pytest.mark.django_db
def test_get_colored_status_if_dup_shop(ticket_factory):
    status = Dictionary.objects.get(code="new")
    ticket = ticket_factory(shop_id="qwe", status=status)
    ticket_factory(shop_id="qwe")
    assert ticket.get_colored_status_if_dup_shop() == "violet colored"


@pytest.mark.django_db
def test_get_colored_status_if_not_dup_shop(ticket_factory):
    status = Dictionary.objects.get(code="new")
    ticket = ticket_factory(shop_id="qwe", status=status)
    assert ticket.get_colored_status_if_dup_shop() is None
