from django.urls import path
from .views import (
    TicketsListView,
    TicketFormView,
    TicketUpdateView,
    CommentCreateView,
    CommentUpdateView,
    DeleteCommentFileView,
    DeleteCommentImageView,
    TicketToWorkView,
    UpdateCommentForReportView,
)


urlpatterns = [
    path("", TicketsListView.as_view(), name="tickets-list"),
    path("new", TicketFormView.as_view(), name="tickets-new"),
    path("<int:pk>/", TicketUpdateView.as_view(), name="ticket-update"),
    path("<int:ticket_pk>/comment", CommentCreateView.as_view(), name="comment-create"),
    path(
        "<int:ticket_pk>/comment/<int:pk>",
        CommentUpdateView.as_view(),
        name="comment-update",
    ),
    path(
        "delete-comment-file/<int:pk>",
        DeleteCommentFileView.as_view(),
        name="delete-comment-file",
    ),
    path(
        "delete-comment-image/<int:pk>",
        DeleteCommentImageView.as_view(),
        name="delete-comment-image",
    ),
    path(
        "comment-toggle-for-report/<int:pk>",
        UpdateCommentForReportView.as_view(),
        name="comment-toggle-for-report",
    ),
    path("to-work/<int:pk>", TicketToWorkView.as_view(), name="ticket-to-work"),
]
