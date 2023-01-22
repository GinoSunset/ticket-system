from typing import Union

from django.db.models import QuerySet
from django.views.generic import ListView, UpdateView
from django.views.generic.edit import CreateView

from django.contrib.auth.mixins import LoginRequiredMixin

from users.models import Operator, Customer, User, Contractor
from additionally.models import Dictionary
from .models import Ticket, Comment, CommentFile
from .forms import TicketsForm, CommentForm, TicketsFormOperator
from .mixin import AccessTicketMixin


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
        user: Union[Customer, Operator, Contractor] = self.request.user.get_role_user()
        customer = user.get_customers()

        self.initial.update(
            {
                "creator": user,
                "customer_qs": customer,
                "status": Dictionary.get_status_ticket("work"),
            }
        )
        return self.initial

    def get_form_class(self):
        if self.request.user.is_customer:
            return TicketsFormOperator
        return self.form_class

    def form_valid(self, form):
        user = self.request.user
        self.object: Ticket = form.save(commit=False)
        self.object.creator = user
        if user.is_customer:
            self.object.customer = user
        if self.object.status is None:
            self.object.status = Dictionary.objects.get(code="work")
        return super().form_valid(form)


class TicketUpdateView(LoginRequiredMixin, AccessTicketMixin, UpdateView):
    model = Ticket
    form_class = TicketsForm
    template_name = "ticket/ticket_update.html"

    def get_initial(self):
        customer = Customer.objects.all()
        user: Union[Customer, Operator, Contractor] = self.request.user.get_role_user()
        customer = user.get_customers()

        self.initial.update({"creator": user, "customer_qs": customer})
        return self.initial


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "ticket/comment_form.html"

    def form_valid(self, form):
        ticket: Ticket = Ticket.objects.get(pk=self.kwargs.get("ticket_pk"))
        self.object: Comment = form.save(commit=False)
        files = self.request.FILES.getlist("files")

        self.object.ticket = ticket
        self.object.author = self.request.user
        self.object: Comment = form.save()
        for file in files:
            CommentFile.objects.create(file=file, comment=self.object)
        return super().form_valid(form)
