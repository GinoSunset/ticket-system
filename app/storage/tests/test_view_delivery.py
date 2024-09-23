import pytest
import datetime

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
    view.today = datetime.date.today()
    view.object = delivery

    view.add_to_stock_component_delivery()

    assert Component.objects.filter(component_type=ct, is_stock=True).count() == 2


@pytest.mark.django_db
def test_delivery_done_append_component_if_date_delivery_was_not_change(
    component_factory, free_component, delivery_factory
):
    "Проверяет что после завершении доставки компонент добавляется на склад если дата доставки не изменилась"
    today = datetime.date.today()
    delivery = delivery_factory(date_delivery=today)
    ct = free_component.component_type
    component_in_del = component_factory(
        delivery=delivery,
        component_type=ct,
        is_stock=False,
    )
    view = DoneDelivery()
    view.today = datetime.date.today()
    view.object = delivery

    view.update_delivery()

    assert Component.objects.filter(component_type=ct, is_stock=True).count() == 2
