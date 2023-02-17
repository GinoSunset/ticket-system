import pytest

from reports.models import Report

from additionally.models import Dictionary


@pytest.mark.django_db
def test_create_excel_file(ticket_factory, report_factory):
    status = Dictionary.get_status_ticket("done")
    ticket = ticket_factory(status=status)
    report: Report = report_factory()
    report.create_report()
