import pytest
import factory

from ticket.models import Comment, CommentFile, CommentImage
from notifications.utils import get_attachments
from django.db.models import signals
from django.core.files.uploadedfile import SimpleUploadedFile


@factory.django.mute_signals(signals.post_save)
@pytest.mark.django_db
def test_attachments_under_max_size(
    comment_factory, notification_factory, redis, file_1_mb, file_5_mb, operator, ticket
):
    comment: Comment = comment_factory(is_for_report=True)
    comment.files.create(file=SimpleUploadedFile("file_1_mb", file_1_mb.read_bytes()))
    comment.files.create(file=SimpleUploadedFile("file_5_mb", file_5_mb.read_bytes()))
    notification = notification_factory(user=operator, ticket=comment.ticket)
    files_to_attach, files_as_links = get_attachments(
        notification, max_email_size=2048 * 1024
    )
    assert len(files_to_attach) == 1
    assert len(files_as_links) == 1
    assert isinstance(files_to_attach[0], CommentFile)
    assert isinstance(files_as_links[0], str)


@factory.django.mute_signals(signals.post_save)
@pytest.mark.django_db
def test_attachments_small_size(
    comment_factory, notification_factory, redis, file_1_mb, file_5_mb, operator, ticket
):
    comment: Comment = comment_factory(is_for_report=True)
    comment.files.create(file=SimpleUploadedFile("file_1_mb", file_1_mb.read_bytes()))
    comment.images.create(image=SimpleUploadedFile("file_5_mb", file_5_mb.read_bytes()))
    notification = notification_factory(user=operator, ticket=comment.ticket)
    files_to_attach, files_as_links = get_attachments(
        notification, max_email_size=2048 * 10024
    )
    assert len(files_to_attach) == 2
    assert len(files_as_links) == 0
    assert isinstance(files_to_attach[0], CommentFile)
    assert isinstance(files_to_attach[1], CommentImage)


@factory.django.mute_signals(signals.post_save)
@pytest.mark.django_db
def test_attachments_all_large_size(
    comment_factory, notification_factory, redis, file_1_mb, file_5_mb, operator, ticket
):
    comment: Comment = comment_factory(is_for_report=True)
    comment.files.create(file=SimpleUploadedFile("file_1_mb", file_1_mb.read_bytes()))
    comment.images.create(image=SimpleUploadedFile("file_5_mb", file_5_mb.read_bytes()))
    notification = notification_factory(user=operator, ticket=comment.ticket)
    files_to_attach, files_as_links = get_attachments(notification, max_email_size=1)
    assert len(files_to_attach) == 0
    assert len(files_as_links) == 2
    assert isinstance(files_as_links[0], str)
    assert isinstance(files_as_links[1], str)
