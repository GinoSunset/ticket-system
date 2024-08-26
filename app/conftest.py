import pytest
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.core.container import DockerContainer


from pytest_factoryboy import register
from ticket.factory import TicketFactory, CommentFactory
from additionally.models import Dictionary
from notifications.tasks import send_email, send_email_task, send_telegram_notify_task
from django.conf import settings

from notifications.telegram import send_telegram_notify_handler
from notifications.factory import NotificationFactory
from users.factory import (
    UserFactory,
    CustomerFactory,
    OperatorFactory,
    ContractorFactory,
    CustomerProfileFactory,
)
from reports.factories import ReportFactory, ActFactory
from share.factories import ShareFactory

from manufactures.factories import (
    ManufactureFactory,
    NomenclatureFactory,
    ClientManufFactory,
)
from manufactures.tasks import (
    reservation_component_from_nomenclature,
    reserve_components,
)

from storage.factories import (
    ComponentTypeFactory,
    ComponentFactory,
    DeliveryFactory,
    TagComponentFactory,
)

register(TicketFactory)
register(UserFactory)
register(CustomerFactory)
register(CustomerProfileFactory)
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
register(DeliveryFactory)
register(TagComponentFactory)


@pytest.fixture
def monkeypatch_delay_send_email_on_celery(monkeypatch, redis):
    def mock_delay(*args, **kwargs):
        return send_email(*args, **kwargs)

    monkeypatch.setattr(send_email_task, "delay", mock_delay)


@pytest.fixture
def monkeypatch_delay_send_telegram_on_celery(monkeypatch):
    def mock_delay(*args, **kwargs):
        return send_telegram_notify_handler(*args, **kwargs)

    monkeypatch.setattr(send_telegram_notify_task, "delay", mock_delay)


@pytest.fixture
def monkeypatch_delay_reserve_component_celery(monkeypatch):
    def mock_delay(*args, **kwargs):
        return reserve_components(*args, **kwargs)

    monkeypatch.setattr(reservation_component_from_nomenclature, "delay", mock_delay)


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


@pytest.fixture(scope="session")
def redis():
    with DockerContainer("redis:latest").with_name("redis").with_bind_ports(
        6379, 6379
    ) as redis:
        wait_for_logs(redis, "Ready to accept connections")
        yield redis


@pytest.fixture(scope="session")
def rabbitmq():
    with DockerContainer("rabbitmq:3-management").with_name("rabbit").with_bind_ports(
        5672, 5672
    ).with_env("RABBITMQ_DEFAULT_USER", settings.RABBIT_LOGIN).with_env(
        "RABBITMQ_DEFAULT_PASS", settings.RABBIT_PASSWORD
    ).with_env(
        "RABBITMQ_DEFAULT_VHOST", settings.RABBIT_VHOST
    ) as rabbitmq:
        yield rabbitmq


@pytest.fixture(scope="session")
def celery(rabbitmq, redis):
    with DockerContainer("helpdesk").with_env(
        "CELERY_BROKER_URL",
        f"amqp://{settings.RABBIT_LOGIN}:{settings.RABBIT_PASSWORD}@rabbit:{settings.RABBIT_PORT}/{settings.RABBIT_VHOST}",
    ).with_env("CELERY_ACCEPT_CONTENT", settings.CELERY_ACCEPT_CONTENT).with_env(
        "CELERY_RESULT_SERIALIZER", settings.CELERY_RESULT_SERIALIZER
    ).with_env(
        "CELERY_TASK_SERIALIZER", settings.CELERY_TASK_SERIALIZER
    ).with_env(
        "DATABASE_URL", settings.DATABASE_URL.replace("127.0.0.1", "db")
    ).with_command(
        "celery -A ticsys worker -l info"
    ).with_kwargs(
        links={"rabbit": "rabbit", "hdp": "db"}
    ) as celery:
        wait_for_logs(celery, "ready.")
        yield celery


@pytest.fixture(autouse=True)
def setup_test_env(settings):
    settings.TG_BOT_NOTIFICATION_URI = "https://test.com"


@pytest.fixture
def operator_client(operator, client):
    """фикстура для отправки запроса от имени оператора"""
    client.force_login(operator)
    return client


@pytest.fixture
def file_5_mb(tmp_path):
    filename = tmp_path / "big_file.jpg"
    size_in_mb = 5

    # Generate the big file
    with open(filename, "wb") as f:
        f.seek(size_in_mb * 1024 * 1024 - 1)
        f.write(b"\0")

    return filename


@pytest.fixture
def file_1_mb(tmp_path):
    filename = tmp_path / "small_file.txt"
    size_in_mb = 1

    # Generate the big file
    with open(filename, "wb") as f:
        f.seek(size_in_mb * 1024 * 1024 - 1)
        f.write(b"\0")

    return filename


@pytest.fixture
def free_component(component_factory):
    return component_factory(
        is_stock=True,
        is_reserve=False,
        date_delivery=None,
        is_archive=False,
        delivery=None,
        nomenclature=None,
    )
