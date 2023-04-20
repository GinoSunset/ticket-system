from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.http import Http404, JsonResponse
from django.views.generic import CreateView, DeleteView, DetailView
from django.urls import reverse_lazy
from ticket.utils import is_image

from ticket.models import Comment, CommentImage, CommentFile
from ticket.mixin import AccessOperatorMixin
from users.models import User
from .models import Share
from .forms import ShareForm, CommentShareForm

from ticket.models import Ticket


class BaseShareView:
    def check_access(self, ticket: Ticket):
        if not self.request:
            return False
        if self.request.user.is_staff:
            return True

        if ticket.customer.profile.linked_operators.filter(
            pk=self.request.user.pk
        ).exists():
            return True
        return False


class ShareCreateView(
    LoginRequiredMixin, AccessOperatorMixin, CreateView, BaseShareView
):
    model = Share
    form_class = ShareForm
    success_url = reverse_lazy("create-share")

    def form_valid(self, form):
        if not self.check_access(form.cleaned_data.get("ticket")):
            return JsonResponse({"error": "Access denied"}, status=403)
        share: Share = form.save(commit=False)
        share.creator = self.request.user
        share.save()

        return JsonResponse({"uuid": share.uuid, "link": share.get_absolute_url()})


class DeleteShareView(
    LoginRequiredMixin, AccessOperatorMixin, DeleteView, BaseShareView
):
    model = Share
    success_url = reverse_lazy("create-share")
    queryset = Ticket.objects.all()

    def get_object(self):
        ticket = super().get_object()
        if ticket.share:
            obj = ticket.share
            return obj
        raise Http404(
            _("No %(verbose_name)s found matching the query")
            % {"verbose_name": queryset.model._meta.verbose_name}
        )

    def form_valid(self, form):
        if not self.check_access(self.object.ticket):
            return JsonResponse({"error": "Access denied"}, status=403)
        super().form_valid(form)
        return JsonResponse({"status": 200})

    def form_invalid(self, form):
        return JsonResponse({"status": "error"}, status_code=400)


class DetailShareView(DetailView):
    model = Ticket
    template_name = "share/detail.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)

        if self.object.phone:
            kwargs["phones"] = self.object.phone.splitlines()

        return kwargs

    def get_object(self, *args, **kwargs):
        ticket = get_object_or_404(Ticket, share=self.kwargs["pk"])
        return ticket


class ShareCommentCreateView(CreateView):
    model = Comment
    form_class = CommentShareForm

    def form_valid(self, form):
        ticket: Ticket = Ticket.objects.get(pk=self.kwargs.get("ticket_pk"))
        self.object: Comment = form.save(commit=False)
        files = self.request.FILES.getlist("files")

        self.object.ticket = ticket
        self.object.author = self.get_or_create_user(
            form.cleaned_data.get("user_fingerprint")
        )
        self.object: Comment = form.save()
        for file in files:
            if is_image(file):
                CommentImage.objects.create(image=file, comment=self.object)
                continue
            CommentFile.objects.create(file=file, comment=self.object)
        return super().form_valid(form)

    def get_or_create_user(self, fingerprint):
        if not fingerprint:
            user = User.objects.create(
                username="without_fingerprint",
                is_active=False,
                first_name="Неопознанный",
                last_name="Пользователь",
            )
            user.last_name = "Пользователь %s" % user.pk
            user.save(update_fields=["last_name"])
            return user
        user, created = User.objects.get_or_create(
            username=fingerprint,
            defaults={
                "is_active": False,
                "first_name": "Неопознанный",
                "last_name": "Пользователь",
                "role": User.Role.OTHER,
            },
        )
        if not created:
            user.last_name = "Пользователь %s" % user.pk
            user.save(update_fields=["last_name"])
        return user
