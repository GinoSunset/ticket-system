from typing import Union

from django.db.models import QuerySet
from django.views.generic import ListView, UpdateView, DeleteView, View
from django.views.generic.edit import CreateView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from reports.models import Act

from users.models import Operator, Customer, User, Contractor
from additionally.models import Dictionary

from notifications.models import Notification
from share.logics import create_share, remove_share, processing_share
from .models import Ticket, Comment, CommentFile, CommentImage
from .forms import TicketsForm, CommentForm, TicketsFormCustomer
from .mixin import AccessTicketMixin, AccessAuthorMixin, AccessOperatorMixin
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = Dictionary.status_tickets()
        return context


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
            return TicketsFormCustomer
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

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)

        if self.object.phone:
            kwargs["phones"] = self.object.phone.splitlines()
        if not self.request.user.is_operator:
            kwargs.pop("form")
        if self.request.user.is_operator:
            kwargs["form_comment_to_report"] = CommentForm(
                initial={"is_for_report": True}
            )
        return kwargs

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
            processing_share(self.object, self.request.user)
        return result

    def create_comment_from_change_ticket(self, form):
        changed_data = form.changed_data
        initial_data = form.initial
        named_field = {field: form[field].label.lower() for field in form.fields}
        ticket = form.instance
        text = Comment.get_text_system_comment(
            changed_data, initial_data, named_field, ticket
        )
        Comment.create_update_system_comment(text, ticket, self.request.user)
        Notification.create_notify_update_ticket(form.changed_data, form.instance)


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

    def get_author(self):
        obj = self.get_object()
        return obj.author

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


class DeleteCommentFileView(LoginRequiredMixin, AccessAuthorMixin, DeleteView):
    model = CommentFile
    template_name = "ticket/comment_file_delete.html"

    def get_author(self):
        obj = self.get_object()
        return obj.comment.author

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["url_delete_name"] = "delete-comment-file"
        return kwargs

    def get_success_url(self):
        return reverse("ticket-update", kwargs={"pk": self.object.comment.ticket.pk})


class DeleteCommentImageView(LoginRequiredMixin, AccessAuthorMixin, DeleteView):
    model = CommentImage
    template_name = "ticket/comment_file_delete.html"

    def get_author(self):
        obj = self.get_object()

        return obj.comment.author

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["url_delete_name"] = "delete-comment-image"
        return kwargs

    def get_success_url(self):
        return reverse("ticket-update", kwargs={"pk": self.object.comment.ticket.pk})


class TicketToWorkView(LoginRequiredMixin, AccessOperatorMixin, View):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        ticket: Ticket = Ticket.objects.get(pk=kwargs.get("pk"))
        status_work = Dictionary.get_status_ticket("work")
        message = Comment.TEMPLATE_DICT.get("status")
        message = message.format(
            field="статус",
            prev_value=ticket.status.description,
            value=status_work.description,
        )
        responsible_msg = Comment.TEMPLATE_DICT.get("responsible")
        responsible_msg = responsible_msg.format(value=user)
        message += responsible_msg
        ticket.status = status_work
        ticket.responsible = request.user
        ticket.save()

        Notification.create_notify_for_customer_when_ticket_to_work(ticket)
        Comment.create_update_system_comment(message, ticket, user)
        create_share(ticket, request.user)

        return redirect("ticket-update", pk=ticket.pk)


class TicketToDoneView(LoginRequiredMixin, AccessOperatorMixin, View):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        ticket: Ticket = Ticket.objects.get(pk=kwargs.get("pk"))
        status_done = Dictionary.get_status_ticket("done")
        message = Comment.TEMPLATE_DICT[("status")]
        message = message.format(
            field="статус",
            prev_value=ticket.status.description,
            value=status_done.description,
        )
        ticket.status = status_done
        ticket.save()

        Notification.create_notify_for_customer_when_ticket_to_done(ticket)
        Comment.create_update_system_comment(message, ticket, user)
        remove_share(ticket=ticket)
        return redirect("ticket-update", pk=ticket.pk)


class TicketToCancelView(LoginRequiredMixin, AccessOperatorMixin, View):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        ticket: Ticket = Ticket.objects.get(pk=kwargs.get("pk"))
        status_cancel = Dictionary.get_status_ticket("cancel")
        message = Comment.TEMPLATE_DICT[("status")]
        message = message.format(
            field="статус",
            prev_value=ticket.status.description,
            value=status_cancel.description,
        )
        ticket.status = status_cancel
        ticket.save()

        Notification.create_notify_for_customer_when_ticket_to_cancel(ticket)
        Comment.create_update_system_comment(message, ticket, user)
        remove_share(ticket=ticket)

        return redirect("ticket-update", pk=ticket.pk)


class TicketCreateAct(LoginRequiredMixin, AccessOperatorMixin, View):
    def get(self, request, *args, **kwargs):
        ticket: Ticket = Ticket.objects.get(pk=kwargs.get("pk"))
        if not hasattr(ticket, "act"):
            act = Act.objects.create(ticket=ticket)
            ticket.refresh_from_db()
        ticket.act.create_act()
        return redirect("ticket-update", pk=ticket.pk)


class UpdateCommentForReportView(LoginRequiredMixin, AccessOperatorMixin, View):
    def get(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs.get("pk"))
        comment.is_for_report = not comment.is_for_report
        comment.save()
        return redirect("ticket-update", pk=comment.ticket.pk)
