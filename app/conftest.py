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
    InvoiceFactory,
    InvoiceAliasRelationFactory,
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
register(InvoiceFactory)
register(InvoiceAliasRelationFactory)

@pytest.fixture
def monkeypatch_delay_send_email_on_celery(monkeypatch, redis):
    def mock_delay(*args, **kwargs):
        return send_email(*args, **kwargs)

    monkeypatch.setattr(send_email_task, "delay", mock_delay)


@pytest.fixture
def monkeypatch_delay_send_telegram_on_celery(monkeypatch):
    def mock_delay(*args, **kwargs):
        return run_sent_to_parse_invoice(args[1][0], **kwargs)

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
