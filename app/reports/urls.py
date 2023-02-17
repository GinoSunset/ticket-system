from django.urls import path
from .views import CreateReportView, DownloadReport, ReportListView


urlpatterns = [
    path("create", CreateReportView.as_view(), name="create-report"),
    path("download-report/<int:pk>", DownloadReport.as_view(), name="download-report"),
    path("", ReportListView.as_view(), name="report-list"),
]
