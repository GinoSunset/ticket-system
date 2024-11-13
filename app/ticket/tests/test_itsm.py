from django.urls import reverse
import factory
import pytest
from ticket.forms import CommentForm
from ticket.handlers_itsm import (
    create_task_from_itsm,
    get_info_about_personal_customer,
    get_info_about_shop,
    get_tickets_for_update,
    send_comment_to_itsm,
    updates_itsm_tickets,
)
from ticket.models import Comment, Ticket
from ticket.signals import send_ticket_to_channel, send_ticket_to_operators
from django.db.models.signals import post_save


@factory.django.mute_signals(post_save)
@pytest.mark.django_db
def test_create_task_from_itsm(mock_itsm_request, dm_customer):
    create_task_from_itsm()
    count_task_in_json = 4
    # save_task_from_itsm(tasks)
    assert Ticket.objects.count() == count_task_in_json


def test_get_info_about_personal_customer(mock_itsm_request):
    personals_info = get_info_about_personal_customer({"link": "http://test.com/employee/test-id"})
    personal_info = personals_info[0]
    assert personal_info.get("display_name") is not None
    assert personal_info.get("c_ldap_position") is not None
    assert personal_info.get("mobile_phone") is not None


def test_get_info_about_shop(mock_itsm_request):
    shop_info = get_info_about_shop({"link": "***************/org_unit/test-id"})
    assert shop_info.city is None
    assert shop_info.shop_id is not None
    assert shop_info.address is None


@factory.django.mute_signals(post_save)
@pytest.mark.django_db
def test_update_itsm_ticket_comment(mock_itsm_request, ticket: Ticket, status_in_work):
    ticket.source_ticket = ticket.SourceTicket.ITSM
    ticket.status = status_in_work
    ticket.save()
    assert ticket.comments.count() == 0

    updates_itsm_tickets()

    ticket.refresh_from_db()
    assert ticket.comments.count() > 0


@factory.django.mute_signals(post_save)
@pytest.mark.django_db
def test_get_itsm_ticket_for_update_comment(ticket_factory, status_in_work, status_new, status_done):
    ticket_itsm_new = ticket_factory(source_ticket=Ticket.SourceTicket.ITSM, status=status_new)
    ticket_itsm_done = ticket_factory(source_ticket=Ticket.SourceTicket.ITSM, status=status_done)
    ticket_itsm_work = ticket_factory(source_ticket=Ticket.SourceTicket.ITSM, status=status_in_work)
    ticket_email = ticket_factory(source_ticket=Ticket.SourceTicket.EMAIL, status=status_new)

    tickets = get_tickets_for_update()

    ids = {i.pk for i in tickets}
    must_be_in_tickets = {ticket_itsm_new.pk, ticket_itsm_work.pk}
    not_be_in_tickets = {ticket_itsm_done, ticket_email}

    assert ids == must_be_in_tickets
    assert not any([i not in ids for i in not_be_in_tickets])


class TestComment:
    @pytest.mark.django_db
    @factory.django.mute_signals(post_save)
    def test_create_comment_with_sent_to_itsm_update_id_itsm(self, comment_factory, mock_itsm_request_comment):
        comment: Comment = comment_factory(is_for_itsm_sent=True)
        send_comment_to_itsm(comment=comment)
        comment.refresh_from_db()
        assert comment.status_itsm_push is not None

    @factory.django.mute_signals(post_save)
    @pytest.mark.django_db
    def test_create_comment_from_form(self, ticket_factory, operator_client):
        ticket = ticket_factory(source_ticket=Ticket.SourceTicket.ITSM)
        url = reverse("comment-create", kwargs={"ticket_pk": ticket.pk})
        form_data = {
            "text": "Updated text",
            "is_for_itsm_sent": True,
        }
        response = operator_client.post(url, data=form_data)

        assert response.status_code == 302

        comment = Comment.objects.last()
        assert comment
        assert comment.text == form_data["text"]
        assert comment.is_for_itsm_sent is True
