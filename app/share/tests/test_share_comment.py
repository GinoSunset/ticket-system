import pytest

from django.urls import reverse
from ticket.models import Comment

from users.models import User


@pytest.mark.django_db
def test_create_share_comment(client, share_factory, ticket_factory):
    ticket = ticket_factory()
    share = share_factory(ticket=ticket)

    response = client.post(
        reverse(
            "comment-share",
            kwargs={"pk": share.pk, "ticket_pk": ticket.pk},
        ),
        data={
            "text": "test",
            "user_fingerprint": "test-fingerprint",
        },
    )
    assert response.status_code == 302
    assert Comment.objects.count() == 1
    comment = Comment.objects.first()
    assert comment
    assert comment.text == "test"
    assert comment.author.username == "test-fingerprint"
    assert comment.author.first_name == "Неопознанный"
    assert "Пользователь" in comment.author.last_name
    assert comment.author.role == User.Role.OTHER
    assert comment.author.is_active == False
    assert comment.ticket == ticket
