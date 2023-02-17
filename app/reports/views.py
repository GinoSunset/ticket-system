from django.shortcuts import render
from django.views.generic import FormView

from .forms import CreateReportForm


class CreateReportView(FormView):
    template_name = "reports/create.html"
    form_class = CreateReportForm
    success_url = "/reports/"

    def form_valid(self, form):
        report = form.save(commit=False)
        report.user = self.request.user
        report.create_report()
        return super(CreateReportView, self).form_valid(form)
