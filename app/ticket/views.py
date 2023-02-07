from typing import Union

from django.db.models import QuerySet
from django.views.generic import ListView, UpdateView
from django.views.generic.edit import CreateView

from django.contrib.auth.mixins import LoginRequiredMixin

from users.models import Operator, Customer, User, Contractor
from additionally.models import Dictionary
from .models import Ticket, Comment, CommentFile, CommentImage
from .forms import TicketsForm, CommentForm, TicketsFormOperator
from .mixin import AccessTicketMixin, AccessAuthorMixin
from .utils import is_image


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
                "type_ticket": Dictionary.get_type_ticket(Ticket.default_type_code),
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
        self.initial = super().get_initial()
        customer = Customer.objects.all()
        user: Union[Customer, Operator, Contractor] = self.request.user.get_role_user()
        customer = user.get_customers()

        self.initial.update(
            {
                "creator": user,
                "customer_qs": customer,
                "status": self.object.status,
            }
        )
        return self.initial

    def form_valid(self, form: TicketsForm):
        result = super().form_valid(form)
        if form.changed_data:
            self.create_comment_from_change_ticket(form)
        return result

    def create_comment_from_change_ticket(self, form):
        template_dict = {
            "status": "{field} изменен c '{prev_value}' на '{value}'\n",
            "contractor": "{value} назначен исполнителем\n",
            "planned_execution_date": "Планируемая дата выезда назначена на: {value}\n",
        }

        text = ""
        for field in form.changed_data:
            value = getattr(form.instance, field)
            value = value if value else "Пусто"
            message = template_dict.get(
                field, "Поле {field} изменено c '{prev_value}' на '{value}'\n"
            )
            text += message.format(
                field=(form.fields[field].label).lower(),
                prev_value=form.initial.get(field, "Пусто") or "Не указано",
                value=value,
            )
        Comment.objects.create(
            ticket=form.instance,
            author=self.request.user,
            text=text,
            is_system_message=True,
        )


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
            if is_image(file):
                CommentImage.objects.create(image=file, comment=self.object)
                continue
            CommentFile.objects.create(file=file, comment=self.object)
        return super().form_valid(form)


class CommentUpdateView(LoginRequiredMixin, AccessAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "ticket/comment_form.html"
    author_field = "author"

    def get_initial(self):
        self.initial.update({"author": self.request.user})
        return self.initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name_page"] = "Изменить комментарий"
        context["name_btn"] = "Изменить"
        return context

    def form_valid(self, form):
        files = self.request.FILES.getlist("files")
        self.object: Comment = form.save(commit=False)
        self.object.is_changed = form.has_changed()
        self.object = form.save()
        for file in files:
            if is_image(file):
                CommentImage.objects.create(image=file, comment=self.object)
                continue
            CommentFile.objects.create(file=file, comment=self.object)
        return super().form_valid(form)
