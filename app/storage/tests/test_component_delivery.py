import datetime
from datetime import timedelta
import pytest
import factory

from django.urls import reverse
from ticket import signals
from storage.models import Delivery, Component
from storage.views import DeliveryUpdateView, create_delivery_component
from storage.reserve import reserve_component


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
def test_update_delivery_upper_change_reservation(
    component_type_factory,
    manufacture_factory,
    component_factory,
    nomenclature_factory,
    monkeypatch_delay_reserve_component_celery,
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
    assert component.nomenclature is None
    assert component.date_delivery == delivery.date_delivery

    assert Component.objects.filter(
        component_type=ct, is_reserve=True, is_stock=False, nomenclature=nomenclature
    ).exists()


@pytest.mark.django_db
def test_create_delivery_may_reserved_needed_component(
    component_type_factory,
    nomenclature_factory,
    manufacture_factory,
    operator_client,
    monkeypatch_delay_reserve_component_celery,
):
    ct = component_type_factory()

    date_delivery = datetime.date.today()
    manufacture = manufacture_factory(date_shipment=date_delivery)
    nomenclature = nomenclature_factory(
        comment="{" + ct.name + " 1шт}", manufacture=manufacture
    )
    component = Component.objects.filter(
        nomenclature=nomenclature, component_type=ct
    ).first()
    data = {
        "type_count-0-component_type": ct.pk,
        "type_count-0-count": 1,
        "date_delivery": date_delivery,
        "type_count-TOTAL_FORMS": 1,
        "type_count-INITIAL_FORMS": "0",
    }

    res = operator_client.post(reverse("delivery-create"), data=data, format="json")

    component.refresh_from_db()
    assert component.is_reserve
    assert component.date_delivery == date_delivery


@pytest.mark.django_db
def test_update_delivery_change_number_component(
    delivery_factory, operator_client, component_factory, component_type
):
    delivery: Delivery = delivery_factory()
    url = reverse("update_delivery", kwargs={"pk": delivery.pk})
    components = component_factory.create_batch(
        size=3,
        is_stock=False,
        component_type=component_type,
        date_delivery=delivery.date_delivery,
        delivery=delivery,
        is_reserve=False,
        nomenclature=None,
    )

    data = {
        "type_count-0-component_type": component_type.pk,
        "type_count-0-count": "1",
        "date_delivery": delivery.date_delivery,
        "type_count-TOTAL_FORMS": "1",
        "type_count-INITIAL_FORMS": "1",
    }
    res = operator_client.post(url, data=data, format="json")
    assert (
        Component.objects.filter(
            component_type=component_type, delivery=delivery
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_update_delivery_page_has_all_components_count(
    delivery_factory, component_type_factory, component_factory, operator_client
):
    delivery = delivery_factory()
    components = component_factory.create_batch(size=2, delivery=delivery)
    for component in components:
        component_factory(component_type=component.component_type, delivery=delivery)

    url = reverse("update_delivery", kwargs={"pk": delivery.pk})

    res = operator_client.get(url)

    assert len(res.context_data["type_count_forms"]) == 2


@pytest.mark.django_db
def test_downgrade_component_in_delivery(
    component_type,
    component_factory,
    delivery,
    nomenclature_factory,
    monkeypatch_delay_reserve_component_celery,
):
    nomenclature = nomenclature_factory()
    c1 = component_factory(
        delivery=delivery,
        is_reserve=True,
        nomenclature=nomenclature,
        component_type=component_type,
    )
    c2 = component_factory(
        delivery=delivery,
        is_reserve=True,
        nomenclature=nomenclature,
        component_type=component_type,
    )
    c3 = component_factory(
        delivery=delivery,
        is_reserve=False,
        nomenclature=None,
        component_type=component_type,
    )

    DeliveryUpdateView.remove_component_delivery(
        delivery, component_type, count=1, count_in_db=3
    )

    c1.refresh_from_db()
    c2.refresh_from_db()
    assert (
        Component.objects.filter(component_type=component_type, delivery=delivery).get()
        == c1
    )
    assert c2.delivery is None
    assert not Component.objects.filter(pk=c3.pk).exists()


@pytest.mark.django_db
def test_create_delivery_component_reserve_many_component(
    component_type,
    component_factory,
    delivery_factory,
    nomenclature_factory,
    manufacture_factory,
    monkeypatch_delay_reserve_component_celery,
):
    manufacture = manufacture_factory(date_shipment=datetime.date.today())
    nomenclature = nomenclature_factory(manufacture=manufacture)
    components = component_factory.create_batch(
        size=4,
        component_type=component_type,
        nomenclature=nomenclature,
        is_reserve=True,
        delivery=None,
        date_delivery=None,
    )
    delivery = delivery_factory(date_delivery=manufacture.date_shipment)

    create_delivery_component(delivery=delivery, count=5, cmnt_type=component_type)

    assert (
        Component.objects.filter(
            delivery__isnull=False, nomenclature=nomenclature
        ).count()
        == 4
    )
    assert Component.objects.filter(delivery__isnull=False).count() == 5


@pytest.mark.django_db
def test_done_delivery_send_component_to_stock(
    operator_client, delivery, component_type, component_factory
):
    components = component_factory(component_type=component_type, delivery=delivery)
    url = reverse("done_delivery", kwargs={"pk": delivery.pk})
    res = operator_client.post(url)
    assert res.status_code == 201
    assert Component.objects.filter(component_type=component_type, is_stock=True)
    delivery.refresh_from_db()
    assert delivery.status == Delivery.Status.DONE


@pytest.mark.django_db
def test_re_reserve_component_if_ahead_delivery(
    manufacture_factory,
    nomenclature_factory,
    delivery_factory,
    component_type,
    component_factory,
    operator_client,
    monkeypatch_delay_reserve_component_celery,
):
    manufacture = manufacture_factory(
        date_shipment=(datetime.date.today() + timedelta(days=1))
    )
    nomenclature = nomenclature_factory(
        manufacture=manufacture, comment="{" + component_type.name + " 2шт}"
    )
    delivery = delivery_factory(
        date_delivery=datetime.date.today() + timedelta(days=10)
    )
    component = component_factory(
        nomenclature=None,
        is_stock=False,
        delivery=delivery,
        date_delivery=delivery.date_delivery,
        component_type=component_type,
    )
    url = reverse("done_delivery", kwargs={"pk": delivery.pk})

    res = operator_client.post(url)

    assert Component.objects.filter(
        nomenclature=nomenclature,
        delivery=delivery,
        component_type=component_type,
        is_stock=True,
    ).exists()
    assert Component.objects.filter(pk=component.pk).exists() is False


@pytest.mark.django_db
def test_re_reserve_component_if_ahead_delivery_has_more_one_component(
    manufacture_factory,
    nomenclature_factory,
    delivery_factory,
    component_type,
    component_factory,
    operator_client,
    monkeypatch_delay_reserve_component_celery,
):
    manufacture = manufacture_factory(
        date_shipment=(datetime.date.today() + timedelta(days=1))
    )
    nomenclature = nomenclature_factory(
        manufacture=manufacture, comment="{" + component_type.name + " 1шт}"
    )
    delivery = delivery_factory(
        date_delivery=datetime.date.today() + timedelta(days=10)
    )
    components = component_factory.create_batch(
        size=2,
        nomenclature=None,
        is_stock=False,
        delivery=delivery,
        date_delivery=delivery.date_delivery,
        component_type=component_type,
    )
    url = reverse("done_delivery", kwargs={"pk": delivery.pk})

    res = operator_client.post(url)

    assert (
        Component.objects.filter(
            nomenclature=nomenclature,
            delivery=delivery,
            component_type=component_type,
            is_stock=True,
        ).count()
        == 1
    )
    assert (
        Component.objects.filter(
            component_type=component_type,
            nomenclature__isnull=True,
            delivery=delivery,
            is_stock=True,
        ).count()
        == 1
    )


@factory.django.mute_signals(signals.post_save)
@pytest.mark.django_db
def test_ticket_phantom_component_change_to_delivery_when_create_delivery(
    ticket_factory, customer_profile_factory, component_type
):
    """
    Проверяет что фантомные (недостающие) компоненты из задачи будут при создании доставки будут
    перерезервированы компонентами из доставки
    """
    ticket = ticket_factory()
    customer_profile_factory(user=ticket.customer)
    reserve_component(component_type, ticket)
