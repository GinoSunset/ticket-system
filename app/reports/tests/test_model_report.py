import pytest

from reports.models import Report
from datetime import datetime
from additionally.models import Dictionary


@pytest.mark.django_db
def test_take_needed_tickets_without_compiled_date(ticket_factory, report_factory):
    status = Dictionary.get_status_ticket("done")
    ticket = ticket_factory(
        status=status,
        date_update=datetime.strptime("2020-01-31", "%Y-%m-%d"),
    )
    ticket.date_create = datetime.strptime("2020-01-01", "%Y-%m-%d")
    ticket.save()
    ticket.refresh_from_db()
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
        date_update=datetime.strptime("2020-01-31", "%Y-%m-%d"),
        completion_date=datetime.strptime("2020-01-30", "%Y-%m-%d"),
    )
    ticket.date_create = datetime.strptime("2020-01-01", "%Y-%m-%d")
    ticket.save()
    ticket.refresh_from_db()

    report: Report = report_factory(
        start_date=ticket.date_create, end_date=ticket.completion_date
    )
    tickets = report.get_tickets_to_report()
    assert tickets.count() == 1
    assert tickets[0].sap_id == ticket.sap_id


@pytest.mark.django_db
def test_not_take_ticket_with_type_warranty(ticket_factory, report_factory):

    type_ticket = Dictionary.get_type_ticket("warranty")
    status = Dictionary.get_status_ticket("done")
    ticket = ticket_factory(
        status=status,
        date_update=datetime.strptime("2020-01-31", "%Y-%m-%d"),
        completion_date=datetime.strptime("2020-01-30", "%Y-%m-%d"),
        type_ticket=type_ticket,
    )
    ticket.date_create = datetime.strptime("2020-01-01", "%Y-%m-%d")
    ticket.save()
    ticket.refresh_from_db()

    report: Report = report_factory(
        start_date=ticket.date_create, end_date=ticket.completion_date
    )
    tickets = report.get_tickets_to_report()
    assert tickets.count() == 0


@pytest.mark.django_db
def test_success_get_comment_for_report(
    ticket_factory, comment_factory, report_factory
):
    ticket = ticket_factory()
    size_comment_for_report = 3
    comments = comment_factory.create_batch(
        size=size_comment_for_report, ticket=ticket, is_for_report=True
    )
    comment_factory(is_for_report=False)
    report: Report = report_factory()

    comments_str = report.get_comments(ticket)
    assert len(comments_str.split(report.COMMENT_SEP)) == size_comment_for_report
