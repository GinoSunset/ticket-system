import datetime
import pytest

from django.urls import reverse
from storage.models import Delivery


@pytest.mark.django_db
def test_delivery_create(admin_client, client, operator, component_type_factory):
    ct = component_type_factory()
    delivery_date = datetime.date(2020, 1, 1)
    data = {"component_type_1": ct.pk, "count_1": 10, "date_delivery": delivery_date}
    # TODO:change to login
    # client.force_login(operator)

    res = admin_client.post(reverse("delivery-create"), json=data)
    assert res.status_code == 200
    assert Delivery.objects.filter(date_delivery=delivery_date).exists()
    assert False
