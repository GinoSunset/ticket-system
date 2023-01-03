from typing import Union

from django.db.models import QuerySet
from django.views.generic import ListView, UpdateView
from django.views.generic.edit import CreateView

from django.contrib.auth.mixins import LoginRequiredMixin

from users.models import Operator, Customer, User, Contractor
from .models import Ticket
from .forms import TicketsForm


class TicketsListView(LoginRequiredMixin, ListView):
    model = Ticket
    ordering = "-date_create"

    def get_queryset(self) -> QuerySet[Ticket]:
        queryset = super().get_queryset()
        user: Union[Customer, Contractor, Operator] = self.request.user.get_role_user()
        if user.is_staff:
            return queryset
        filter_from_user: dict = user.get_ticket_filter() or {}
        return queryset.filter(**filter_from_user)


class TicketFormView(LoginRequiredMixin, CreateView):
    form_class = TicketsForm
    template_name = "ticket/ticket_form.html"

    def get_initial(self):
        customer = Customer.objects.all()
        if self.request.user.is_operator:
            operator = self.request.user.get_role_user()
            customer = operator.get_customers()
        self.initial.update({"creator": operator, "customer_qs": customer})
        return self.initial


class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    form_class = TicketsForm
    template_name = "ticket/ticket_update.html"

    def get_initial(self):
        customer = Customer.objects.all()
        if self.request.user.is_operator:
            operator = self.request.user.get_role_user()
            customer = operator.get_customers()
        self.initial.update({"creator": operator, "customer_qs": customer})
        return self.initial
