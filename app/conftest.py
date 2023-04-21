import pytest

from pytest_factoryboy import register
from ticket.factory import TicketFactory, CommentFactory
from additionally.models import Dictionary
from notifications.tasks import send_email, send_email_task

from notifications.factory import NotificationFactory
from users.factory import (
    UserFactory,
    CustomerFactory,
    OperatorFactory,
    ContractorFactory,
)
from reports.factories import ReportFactory, ActFactory
from share.factories import ShareFactory

register(TicketFactory)
register(UserFactory)
register(CustomerFactory)
register(OperatorFactory)
register(ContractorFactory)
register(NotificationFactory)
register(ReportFactory)
register(ActFactory)
register(CommentFactory)
register(ShareFactory)


@pytest.fixture
def monkeypatch_delay_send_email_on_celery(monkeypatch):
    def mock_delay(*args, **kwargs):
        return send_email(*args, **kwargs)

    monkeypatch.setattr(send_email_task, "delay", mock_delay)


@pytest.fixture
def status_done():
    return Dictionary.get_status_ticket("done")


@pytest.fixture
def status_in_work():
    return Dictionary.get_status_ticket("work")
