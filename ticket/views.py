from django.views.generic import ListView

from .models import Ticket


class TicketsListView(ListView):
    model = Ticket
    ordering = "-date_create"
