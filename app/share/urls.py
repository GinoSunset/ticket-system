from django.urls import path
from . import views

urlpatterns = [
    path("", views.ShareCreateView.as_view(), name="create-share"),
]
