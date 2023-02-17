import pytest
from notifications.models import Notification


class TestCreateNotifySignal:
    """Test create notify signal."""

    @pytest.mark.skip
    @pytest.mark.django_db
    def test_create_notify_by_new_ticket(
        self,
        ticket_factory,
        customer_factory,
        operator_factory,
        monkeypatch_delay_send_email_on_celery,
    ):
        """Test create notify by new ticket."""
        operator = operator_factory()
        customer = customer_factory()
        operator.customers.add(customer.profile)
        ticket = ticket_factory(customer=customer)
        assert Notification.objects.filter(user=operator).count() == 1
