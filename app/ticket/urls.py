from django.urls import path
from ticket import views


urlpatterns = [
    path("", views.TicketsListView.as_view(), name="tickets-list"),
    path("new", views.TicketFormView.as_view(), name="tickets-new"),
    path("<int:pk>/", views.TicketUpdateView.as_view(), name="ticket-update"),
    path(
        "<int:ticket_pk>/comment",
        views.CommentCreateView.as_view(),
        name="comment-create",
    ),
    path(
        "<int:ticket_pk>/comment/<int:pk>",
        views.CommentUpdateView.as_view(),
        name="comment-update",
    ),
    path(
        "delete-comment-file/<int:pk>",
        views.DeleteCommentFileView.as_view(),
        name="delete-comment-file",
    ),
    path(
        "delete-comment-image/<int:pk>",
        views.DeleteCommentImageView.as_view(),
        name="delete-comment-image",
    ),
    path(
        "comment-toggle-for-report/<int:pk>",
        views.UpdateCommentForReportView.as_view(),
        name="comment-toggle-for-report",
    ),
    path("to-work/<int:pk>", views.TicketToWorkView.as_view(), name="ticket-to-work"),
    path("to-done/<int:pk>", views.TicketToDoneView.as_view(), name="ticket-to-done"),
    path(
        "to-cancel/<int:pk>",
        views.TicketToCancelView.as_view(),
        name="ticket-to-cancel",
    ),
    path("act-create/<int:pk>", views.TicketCreateAct.as_view(), name="act-create"),
]
