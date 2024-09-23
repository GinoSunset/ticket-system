import pytest
from django.urls import reverse
from reports.forms import ReportForm
from reports.models import Report

from additionally.models import Dictionary


@pytest.mark.django_db
def test_create_report_form(ticket_factory, redis):
    status = Dictionary.get_status_ticket("done")
    ticket = ticket_factory(status=status)
    form = ReportForm(
        data={
            "start_date": "1020-01-01",
            "end_date": "3020-01-31",
        }
    )

    assert form.is_valid() is True


@pytest.mark.django_db
def test_create_report_by_client(client, operator_factory):
    user = operator_factory()
    client.force_login(user)
    response = client.post(
        reverse("create-report"),
        data={
            "start_date": "2020-01-01",
            "end_date": "2020-01-31",
        },
    )

    assert response.status_code == 302
    report = Report.objects.first()
    assert report is not None
    assert report.file is not None
