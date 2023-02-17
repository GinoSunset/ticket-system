from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import FormView, ListView, View
from ticket.mixin import AccessOperatorMixin

from .forms import ReportForm
from .models import Report


class CreateReportView(LoginRequiredMixin, AccessOperatorMixin, FormView):
    template_name = "reports/create.html"
    form_class = ReportForm
    success_url = "/reports/"

    def form_valid(self, form):
        report: Report = form.save(commit=False)
        report.creator = self.request.user
        report.create_report()
        return super(CreateReportView, self).form_valid(form)


class ReportListView(LoginRequiredMixin, AccessOperatorMixin, ListView):
    model = Report
    template_name = "reports/list.html"
    ordering = "-date_create"


class DownloadReport(LoginRequiredMixin, AccessOperatorMixin, View):
    def get(self, request, *args, **kwargs):
        report = Report.objects.get(pk=kwargs["pk"])
        response = HttpResponse(report.file, content_type="application/pdf")
        response["Content-Disposition"] = f"attachment; filename={report.file_name}"
        return response
