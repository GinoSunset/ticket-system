import pytest
from additionally.models import Dictionary
from django.urls import reverse

from ticket.models import Ticket, Comment
from users.models import User


class TestUpdateTicket:
    @pytest.mark.django_db
    def test_save_comment_update_status(self, ticket_factory, user_factory, client):

        user = user_factory()
        status = Dictionary.objects.get(code="work")
        new_status = Dictionary.objects.get(code="done")
        ticket = ticket_factory(creator=user, status=status)
        client.force_login(user=user)
        client.post(
            reverse("ticket-update", kwargs={"pk": ticket.pk}),
            data={"status": new_status.pk, "description": ticket.description},
        )
        comment = Comment.objects.filter(ticket=ticket)
        assert comment.exists()
        assert (
            f"статус изменен c '{status.description}' на '{new_status.description}'"
            in comment.first().text
        )

    @pytest.mark.django_db
    def test_save_comment_update_contractor(self, ticket_factory, user_factory, client):

        user = user_factory()
        contractor = user_factory(role=User.Role.CONTRACTOR)
        status = Dictionary.objects.get(code="work")
        ticket = ticket_factory(creator=user, status=status)
        client.force_login(user=user)
        client.post(
            reverse("ticket-update", kwargs={"pk": ticket.pk}),
            data={
                "contractor": contractor.pk,
                "description": ticket.description,
                "status": status.pk,
            },
        )
        comment = Comment.objects.filter(ticket=ticket)
        assert comment.exists()
        assert f"{contractor} назначен исполнителем" in comment.first().text
