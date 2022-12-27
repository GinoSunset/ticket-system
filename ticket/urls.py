from django.urls import path
from .views import TicketsListView


urlpatterns = [
    path("", TicketsListView.as_view(), name="tickets-list"),
]
