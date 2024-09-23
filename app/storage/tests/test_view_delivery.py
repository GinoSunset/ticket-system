import pytest
from datetime import datetime

from storage.models import Component
from storage.views import DoneDelivery


@pytest.mark.django_db
def test_delivery_done_append_component(
    component_factory, free_component, delivery_factory
):
    "Проверяет что после завершении доставки компонент добавляется на склад"
    delivery = delivery_factory()
    ct = free_component.component_type
    component_in_del = component_factory(
        delivery=delivery,
        component_type=ct,
        is_stock=False,
    )
    view = DoneDelivery()
    view.today = datetime.today()
    view.object = delivery

    view.add_to_stock_component_delivery()

    assert Component.objects.filter(component_type=ct, is_stock=True).count() == 2