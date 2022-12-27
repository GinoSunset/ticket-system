from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Ticket


class TicketsListView(LoginRequiredMixin, ListView):
    model = Ticket
    ordering = "-date_create"
