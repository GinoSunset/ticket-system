from django.urls import reverse
from datetime import datetime, timedelta
from django.db.models import signals


from storage.views import ComponentCreateView
from storage.reserve import processing_reserved_component
from storage.models import Component
import factory
import pytest


@pytest.mark.django_db
def test_exist_storage_list_view(operator_client):
    response = operator_client.get(reverse("component-list"))
    assert response.status_code == 302


@pytest.mark.django_db
class TestComponentCreateView:
    def test_get_component_to_reserve(self, component_factory, component_type_factory):
        component_type = component_type_factory()
        component1 = component_factory(
            component_type=component_type,
            is_reserve=True,
            is_stock=False,
            date_delivery=None,
        )
        component2 = component_factory(
            component_type=component_type,
            is_reserve=True,
            is_stock=True,
            date_delivery=None,
        )
        component3 = component_factory(
            component_type=component_type,
            is_reserve=False,
            is_stock=True,
            date_delivery=None,
        )
        date_delivery = datetime.now().date() + timedelta(days=1)
        component4 = component_factory(
            component_type=component_type,
            is_reserve=True,
            is_stock=False,
            date_delivery=date_delivery,
        )

        view = ComponentCreateView()
        components = view.get_components_to_reserve(component_type)

        assert len(components) == 1
        assert component1 in components
        assert component2 not in components
        assert component3 not in components
        assert component4 not in components

    def test_reserve_component_with_date_shipments(
        self,
        component_type,
        component_factory,
        manufacture_factory,
        nomenclature_factory,
        monkeypatch_delay_reserve_component_celery,
    ):
        date_delivery = datetime.now().date() + timedelta(days=1)
        date_shipment = datetime.now().date() + timedelta(days=2)

        manufacture = manufacture_factory(date_shipment=date_shipment)
        nomenclature = nomenclature_factory(manufacture=manufacture)

        component1 = component_factory(
            component_type=component_type,
            is_reserve=True,
            is_stock=False,
            date_delivery=datetime.now().date() + timedelta(days=100),
            nomenclature=nomenclature,
        )
        component2 = component_factory(
            component_type=component_type,
            is_reserve=True,
            is_stock=False,
            nomenclature=nomenclature,
            date_delivery=None,
        )
        component3 = component_factory(
            component_type=component_type,
            is_reserve=True,
            is_stock=True,
            nomenclature=nomenclature,
            date_delivery=None,
        )

        view = ComponentCreateView()
        components = view.get_components_to_reserve_by_date_delivery(
            component_type, date_delivery
        )
        assert len(components) == 1
        assert component1 not in components
        assert component2 in components
        assert component3 not in components


@pytest.mark.django_db
class TestComponentByNomenclature:
    @factory.django.mute_signals(signals.post_save)
    def test_page_with_components_only_by_nomenclature(
        self, nomenclature_factory, admin_client
    ):
        n = nomenclature_factory()
        processing_reserved_component(n)
        components_n = Component.objects.filter(nomenclature=n)

        res = admin_client.get(reverse("nomenclature-components", kwargs={"pk": n.pk}))
        assert res.status_code == 200
        assert (
            sum([i["count"] for i in res.context_data.get("components")])
            == components_n.count()
        )


@factory.django.mute_signals(signals.post_save)
@pytest.mark.django_db
class TestWriteOffComponent:

    def test_write_off_component(
        self, component_factory, operator_client, component_type
    ):
        to_create = 20

        components = component_factory.create_batch(
            size=to_create, component_type=component_type, is_stock=True
        )

        to_write_off = 3
        data = {"count_write_off": to_write_off}
        url = reverse("write-off", kwargs={"pk": component_type.pk})
        res = operator_client.post(url, data=data, format="json")
        assert res.context_data["in_stock"] == to_create - to_write_off
        assert (
            Component.objects.filter(component_type=component_type).count()
            == to_create - to_write_off
        )

    def test_write_off_only_free_component(
        self, component_factory, component_type, operator_client
    ):
        component_factory.create_batch(
            size=20, component_type=component_type, is_reserve=True
        )
        data = {"component_type": component_type.pk, "count_write_off": 20}
        url = reverse("write-off", kwargs={"pk": component_type.pk})
        res = operator_client.post(url, data=data, format="json")
        assert res.context_data["in_stock"] == 20
        assert Component.objects.filter(component_type=component_type).count() == 20
