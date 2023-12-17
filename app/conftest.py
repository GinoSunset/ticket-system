import pytest

from pytest_factoryboy import register
from ticket.factory import TicketFactory, CommentFactory
from additionally.models import Dictionary
from notifications.tasks import send_email, send_email_task, send_telegram_notify_task

from notifications.telegram import send_telegram_notify_handler
from notifications.factory import NotificationFactory
from users.factory import (
    UserFactory,
    CustomerFactory,
    OperatorFactory,
    ContractorFactory,
)
from reports.factories import ReportFactory, ActFactory
from share.factories import ShareFactory

from manufactures.factories import (
    ManufactureFactory,
    NomenclatureFactory,
    ClientManufFactory,
)

from storage.factories import ComponentTypeFactory, ComponentFactory

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
register(ManufactureFactory)
register(NomenclatureFactory)
register(ClientManufFactory, _name="manufacture_client")
# storage
register(ComponentTypeFactory)
register(ComponentFactory)


@pytest.fixture
def monkeypatch_delay_send_email_on_celery(monkeypatch):
    def mock_delay(*args, **kwargs):
        return send_email(*args, **kwargs)

    monkeypatch.setattr(send_email_task, "delay", mock_delay)


@pytest.fixture
def monkeypatch_delay_send_telegram_on_celery(monkeypatch):
    def mock_delay(*args, **kwargs):
        return send_telegram_notify_handler(*args, **kwargs)

    monkeypatch.setattr(send_telegram_notify_task, "delay", mock_delay)


@pytest.fixture
def mocker_bot_sender(monkeypatch):
    """mock function requests.post to save message to inner dict in bot_sender"""

    class BotSender:
        def __init__(self):
            self.messages = {}
            self.status_code = 200

        def send_message(self, *args, **kwargs):
            json = kwargs["json"]
            self.messages[json["user_id"]] = json["text"]
            return self

    bot_sender = BotSender()
    monkeypatch.setattr("requests.post", bot_sender.send_message)
    return bot_sender


@pytest.fixture
def status_done():
    return Dictionary.get_status_ticket("done")


@pytest.fixture
def status_new():
    return Dictionary.get_status_ticket("new")


@pytest.fixture
def status_in_work():
    return Dictionary.get_status_ticket("work")
