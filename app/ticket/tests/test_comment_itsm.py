import factory
import pytest
from ticket.models import Comment
from ticket.handlers_itsm import send_comment_to_itsm
from ticket.signals import post_save


@pytest.mark.django_db
@factory.django.mute_signals(post_save)
def test_create_comment_with_sent_to_itsm_update_id_itsm(
    comment_factory, mock_itsm_request_comment
):
    comment: Comment = comment_factory(is_for_itsm_sent=True)
    send_comment_to_itsm(comment=comment)
    comment.refresh_from_db()
    assert comment.status_itsm_push is not None
