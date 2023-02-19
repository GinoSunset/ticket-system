import pytest

from reports.models import Report
from datetime import datetime
from additionally.models import Dictionary


@pytest.mark.django_db
def test_take_needed_tickets_without_compiled_date(ticket_factory, report_factory):
    status = Dictionary.get_status_ticket("done")
    ticket = ticket_factory(
        status=status,
        date_create=datetime.strptime("2020-01-01", "%Y-%m-%d"),
        date_update=datetime.strptime("2020-01-31", "%Y-%m-%d"),
    )
    report: Report = report_factory(
        start_date=ticket.date_create, end_date=ticket.date_update
    )
    tickets = report.get_tickets_to_report()
    assert tickets.count() == 1
    assert tickets[0].sap_id == ticket.sap_id


@pytest.mark.django_db
def test_take_needed_tickets_with_compiled_date(ticket_factory, report_factory):
    status = Dictionary.get_status_ticket("done")
    ticket = ticket_factory(
        status=status,
        date_create=datetime.strptime("2020-01-01", "%Y-%m-%d"),
        date_update=datetime.strptime("2020-01-31", "%Y-%m-%d"),
        completion_date=datetime.strptime("2020-01-30", "%Y-%m-%d"),
    )
    report: Report = report_factory(
        start_date=ticket.date_create, end_date=ticket.completion_date
    )
    tickets = report.get_tickets_to_report()
    assert tickets.count() == 1
    assert tickets[0].sap_id == ticket.sap_id


@pytest.mark.django_db
def test_create_report_with_comment(ticket_factory, report_factory, comment_factory):
    status = Dictionary.get_status_ticket("done")

    ticket = ticket_factory(
        status=status,
        date_create=datetime.strptime("2020-01-01", "%Y-%m-%d"),
        date_update=datetime.strptime("2020-01-31", "%Y-%m-%d"),
        completion_date=datetime.strptime("2020-01-30", "%Y-%m-%d"),
    )
    report: Report = report_factory(
        start_date=ticket.date_create, end_date=ticket.completion_date
    )
    comment = comment_factory(report=report)

    assert report.comment
