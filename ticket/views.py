from django.db.models import QuerySet
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Ticket
from .forms import TicketsForm


class TicketsListView(LoginRequiredMixin, ListView):
    model = Ticket
    ordering = "-date_create"

    def get_queryset(self) -> QuerySet[Ticket]:
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(creator=self.request.user)


class TicketFormView(LoginRequiredMixin, CreateView):
    form_class = TicketsForm
    template_name = "ticket/ticket_form.html"


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
