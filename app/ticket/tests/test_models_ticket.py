import pytest
from additionally.models import Dictionary
from django.core.files.uploadedfile import SimpleUploadedFile


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


@pytest.mark.django_db
def test_not_change_date_done_if_status_done(ticket_factory):
    ticket = ticket_factory()
    assert ticket.completion_date is None
    ticket.status = Dictionary.objects.get(code="done")
    ticket.save()
    ticket.refresh_from_db()
    old_date = ticket.completion_date
    assert ticket.completion_date is not None
    ticket.status = Dictionary.objects.get(code="done")
    ticket.save()
    ticket.refresh_from_db()
    assert ticket.completion_date == old_date


@pytest.mark.django_db
def test_not_change_date_to_work_if_status_work(ticket_factory):
    ticket = ticket_factory()
    assert ticket.date_to_work is None
    ticket.status = Dictionary.objects.get(code="work")
    ticket.save()
    ticket.refresh_from_db()
    old_date = ticket.date_to_work
    assert ticket.date_to_work is not None
    ticket.status = Dictionary.objects.get(code="work")
    ticket.save()
    ticket.refresh_from_db()
    assert ticket.date_to_work == old_date


@pytest.mark.django_db
def test_comment_for_report_has_comment_with_empty_text(comment_factory):
    comment = comment_factory(text="", is_for_report=True)
    image = comment.images.create(image=SimpleUploadedFile("test.jpg", b"test"))

    assert comment in comment.ticket.get_comments_for_report()
