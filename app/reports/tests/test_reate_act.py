import tempfile
from django.test import override_settings
import pytest

from django.utils import timezone
from reports.models import Act


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_generate_success_act(
    ticket_factory, customer_factory, act_factory, status_done, redis
):
    customer = customer_factory(phone="+7 (999) 999-99-99")
    customer.profile.company = "ООО Тестовая компания"
    customer.profile.save()
    ticket = ticket_factory(
        city="Москва", customer=customer, phone="+7 (999) 999-99-99"
    )
    ticket.status = status_done
    ticket.save()
    ticket.refresh_from_db()
    act: Act = act_factory(ticket=ticket)
    act.create_act()
    assert act.file_doc_act is not None
