import pytest
import factory

from additionally.models import Dictionary
from django.urls import reverse
from django.db.models import signals

from ticket.models import Comment, Ticket


class TestUpdateTicket:
    @pytest.mark.django_db
    def test_save_comment_update_status(self, ticket_factory, client, operator_factory):

        user = operator_factory()
        status = Dictionary.objects.get(code="work")
        new_status = Dictionary.objects.get(code="done")
        ticket = ticket_factory(creator=user, status=status)
        user.customers.add(ticket.customer.profile)
        client.force_login(user=user)
        res = client.post(
            reverse("ticket-update", kwargs={"pk": ticket.pk}),
            data={
                "status": new_status.pk,
                "description": ticket.description,
                "customer": ticket.customer.pk,
            },
        )
        comment = Comment.objects.filter(ticket=ticket)
        assert comment.exists()
        assert (
            f"статус изменен c '{status.description}' на '{new_status.description}'"
            in comment.first().text
        )

    @pytest.mark.django_db
    def test_save_comment_update_contractor(
        self,
        ticket_factory,
        contractor_factory,
        client,
        operator_factory,
        monkeypatch_delay_send_email_on_celery,
    ):

        user = operator_factory()
        contractor = contractor_factory()
        status = Dictionary.objects.get(code="work")
        ticket = ticket_factory(creator=user, status=status)
        user.customers.add(ticket.customer.profile)
        client.force_login(user=user)
        client.post(
            reverse("ticket-update", kwargs={"pk": ticket.pk}),
            data={
                "contractor": contractor.pk,
                "description": ticket.description,
                "status": status.pk,
                "customer": ticket.customer.pk,
            },
        )
        comment = Comment.objects.filter(ticket=ticket)
        assert comment.exists()
        assert f"{contractor} назначен(а) исполнителем" in comment.first().text

    @pytest.mark.django_db
    def test_update_status_to_work_create_comment(
        self,
        ticket_factory,
        operator_factory,
        client,
        monkeypatch_delay_send_email_on_celery,
    ):
        user = operator_factory()
        status = Dictionary.objects.get(code="new")
        ticket: Ticket = ticket_factory(creator=user, status=status)
        client.force_login(user=user)
        res = client.get(reverse("ticket-to-work", kwargs={"pk": ticket.pk}))
        assert res.status_code == 302
        ticket.refresh_from_db()
        assert ticket.comments.count() == 1
        assert f"статус изменен c " in ticket.comments.first().text
