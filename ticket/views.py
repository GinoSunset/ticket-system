from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Ticket
from .forms import TicketsForm


class TicketsListView(LoginRequiredMixin, ListView):
    model = Ticket
    ordering = "-date_create"


class TicketFormView(LoginRequiredMixin, FormView):
    form_class = TicketsForm
    template_name = "ticket/new_ticket.html"


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
