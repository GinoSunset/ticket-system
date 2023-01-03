from django.urls import path
from .views import TicketsListView, TicketFormView, TicketUpdateView


urlpatterns = [
    path("", TicketsListView.as_view(), name="tickets-list"),
    path("new", TicketFormView.as_view(), name="tickets-new"),
    path("<int:pk>/", TicketUpdateView.as_view(), name="ticket-update"),
]
