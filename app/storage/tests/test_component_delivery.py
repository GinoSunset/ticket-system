import datetime
from datetime import timedelta
import pytest

from django.urls import reverse
from storage.models import Delivery, Component


@pytest.mark.django_db
def test_delivery_create(admin_client, client, operator, component_type_factory):
    ct = component_type_factory()
    count_component = 10
    delivery_date = datetime.date(2020, 1, 1)
    data = {
        "type_count-0-component_type": ct.pk,
        "type_count-0-count": count_component,
        "date_delivery": delivery_date,
        "type_count-TOTAL_FORMS": 1,
        "type_count-INITIAL_FORMS": "0",
    }
    # TODO:change to login
    # client.force_login(operator)

    res = admin_client.post(reverse("delivery-create"), data=data, format="json")
    assert res.status_code == 302
    assert Delivery.objects.filter(date_delivery=delivery_date).exists()
    assert (
        Component.objects.filter(component_type=ct, date_delivery=delivery_date).count()
        == count_component
    )


@pytest.mark.django_db
def test_update_delivery_update_component_delivery_date(
    component_type_factory, component_factory
):
    ct = component_type_factory()
    delivery = Delivery.objects.create(date_delivery=datetime.date.today())
    component: Component = component_factory(
        component_type=ct, delivery=delivery, date_delivery=delivery.date_delivery
    )

    delivery.date_delivery = datetime.date.today() + timedelta(days=10)
    delivery.save()

    component.refresh_from_db()
    assert component.date_delivery == delivery.date_delivery


@pytest.mark.django_db
def test_update_delivery_upper_change_resevation(
    component_type_factory, manufacture_factory, component_factory, nomenclature_factory
):
    ct = component_type_factory()
    date_delivery = datetime.date.today()
    delivery = Delivery.objects.create(date_delivery=date_delivery)
    component = component_factory(
        component_type=ct,
        is_stock=False,
        date_delivery=date_delivery,
        delivery=delivery,
        is_reserve=False,
        nomenclature=None,
    )
    manufacture = manufacture_factory(date_shipment=date_delivery)
    nomenclature = nomenclature_factory(
        manufacture=manufacture, comment="{" + ct.name + " 1шт}"
    )
    component.refresh_from_db()
    assert component.is_reserve
    assert component.nomenclature == nomenclature

    # Change date to up.
    delivery.date_delivery = date_delivery + timedelta(days=10)
    delivery.save()

    # Test component not reserve and has no nomeclature, create new component
    component.refresh_from_db()
    assert not component.is_reserve
    assert component.nomnclature is None
    assert component.date_delivery == delivery.date_delivery

    assert Component.objects.filter(
        component_type=ct, is_reserve=True, is_stock=False, nomenclature=nomenclature
    )


def test_create_delivery_may_reserved_needed_component():
    assert False
