from django.utils.translation import gettext as _
from django.http import Http404, JsonResponse
from django.views.generic import CreateView, DeleteView
from django.urls import reverse, reverse_lazy

from ticket.mixin import AccessOperatorMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Share
from .forms import ShareForm

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
