from django.http import JsonResponse
from django.views.generic import CreateView

from ticket.mixin import AccessOperatorMixin, AccessAuthorMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Share
from .forms import ShareForm


class ShareCreateView(LoginRequiredMixin, AccessOperatorMixin, CreateView):
    model = Share
    form_class = ShareForm
    template_name = "share/share_create.html"

    def check_access(self, form):
        ticket = form.cleaned_data.get("ticket")
        if ticket.creator.profile.linked_operators.filter(
            pk=self.request.user.pk
        ).exists():
            return True
        return False

    def form_valid(self, form):
        if not self.check_access(form):
            return JsonResponse({"error": "Access denied"}, status=403)
        share: Share = form.save(commit=False)
        share.creator = self.request.user
        share.save()

        return JsonResponse(
            {"data": {"uuid": share.uuid, "link": share.get_absolute_url()}}
        )
