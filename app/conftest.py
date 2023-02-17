import pytest

from pytest_factoryboy import register
from ticket.factory import TicketFactory
from notifications.tasks import send_email, send_email_task

from notifications.factory import NotificationFactory
from users.factory import (
    UserFactory,
    CustomerFactory,
    OperatorFactory,
    ContractorFactory,
)
from reports.factories import ReportFactory

register(TicketFactory)
register(UserFactory)
register(CustomerFactory)
register(OperatorFactory)
register(ContractorFactory)
register(NotificationFactory)
register(ReportFactory)


@pytest.fixture
def monkeypatch_delay_send_email_on_celery(monkeypatch):
    def mock_delay(*args, **kwargs):
        return send_email(*args, **kwargs)

    monkeypatch.setattr(send_email_task, "delay", mock_delay)
