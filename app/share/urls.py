from django.urls import path
from . import views

urlpatterns = [
    path("", views.ShareCreateView.as_view(), name="create-share"),
    path("delete/<int:pk>", views.DeleteShareView.as_view(), name="delete-share"),
    path("<uuid:pk>", views.DetailShareView.as_view(), name="detail-share"),
    path(
        "comment/<uuid:pk>/<int:ticket_pk>",
        views.ShareCommentCreateView.as_view(),
        name="comment-share",
    ),
]
