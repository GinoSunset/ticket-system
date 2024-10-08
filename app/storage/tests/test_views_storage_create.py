import pytest
from datetime import date
from django.urls import reverse
from storage.models import Component, ComponentType

from storage.forms import ComponentForm
from storage.views.component import ComponentCreateView


@pytest.mark.django_db
class TestComponentCreateView:
    def test_form_valid_with_non_stock_component(
        self,
        operator_client,
        component_factory,
        manufacture_factory,
        nomenclature_factory,
        monkeypatch_delay_reserve_component_celery,
    ):
        manufacture = manufacture_factory(date_shipment=date(2021, 2, 1))
        nomenclature = nomenclature_factory(manufacture=manufacture)
        needed_component = component_factory(
            is_stock=False,
            is_reserve=True,
            nomenclature=nomenclature,
            serial_number="",
            date_delivery=None,
        )
        form_data = {
            "component_type": needed_component.component_type.pk,
            "is_stock": False,
            "count": 1,
            "generate_serial_number": True,
            "date_delivery": date(2021, 1, 1),
        }
        url = reverse("component-create")
        response = operator_client.post(url, data=form_data)
        assert response.status_code == 302
        needed_component.refresh_from_db()
        assert needed_component.is_stock is False
        assert needed_component.serial_number is not None
        assert needed_component.date_delivery == date(2021, 1, 1)

    def test_form_valid_with_stock_component(self, operator_client, component_factory):
        component = component_factory(
            is_reserve=True, is_stock=False, date_delivery=None
        )
        form_data = {
            "component_type": component.component_type.pk,
            "is_stock": True,
            "count": 1,
        }
        url = reverse("component-create")
        response = operator_client.post(url, data=form_data)
        assert response.status_code == 302
        component.refresh_from_db()
        assert component.is_stock is True

    def test_form_valid_create_new_stock_component(
        self,
        operator_client,
        component_type,
        monkeypatch_delay_reserve_component_celery,
    ):
        form_data = {
            "component_type": component_type.pk,
            "is_stock": True,
            "count": 1,
        }
        url = reverse("component-create")
        response = operator_client.post(url, data=form_data)
        assert response.status_code == 302
        component = Component.objects.filter(component_type=component_type).last()
        assert component.is_stock is True

    def test_form_create_component_more_one_count(
        self, operator_client, component_factory
    ):
        ComponentType.objects.all().delete()

        component = component_factory()
        form_data = {
            "component_type": component.component_type.pk,
            "is_stock": True,
            "count": 2,
        }
        url = reverse("component-create")
        response = operator_client.post(url, data=form_data)
        assert response.status_code == 302
        assert Component.objects.count() == 3

    def test_form_create_save_serial_number(
        self,
        operator_client,
        component_type,
        monkeypatch_delay_reserve_component_celery,
    ):
        form_data = {
            "component_type": component_type.pk,
            "is_stock": True,
            "generate_serial_number": True,
            "count": 2,
        }
        url = reverse("component-create")
        response = operator_client.post(url, data=form_data)
        assert response.status_code == 302
        component, component2 = Component.objects.filter(
            component_type=component_type
        ).order_by("-id")[:2]
        assert component.serial_number is not None
        assert component2.serial_number is not None
        assert component2.serial_number != component.serial_number

    def test_reservation_component_who_not_in_stock_after_add_to_stock(
        self, operator_client, component_factory
    ):
        ComponentType.objects.all().delete()
        component = component_factory(
            is_reserve=True,
            is_stock=False,
            date_delivery=None,
        )
        form_data = {
            "component_type": component.component_type.pk,
            "is_stock": True,
            "count": 1,
        }
        url = reverse("component-create")
        response = operator_client.post(url, data=form_data)
        assert response.status_code == 302
        component.refresh_from_db()
        assert component.is_stock is True
        assert component.is_reserve is True
        assert Component.objects.count() == 1

    def test_reserve_and_create_component_in_delivery(
        self,
        operator_client,
        component_factory,
        nomenclature_factory,
        monkeypatch_delay_reserve_component_celery,
    ):
        ComponentType.objects.all().delete()
        nomenclature = nomenclature_factory(manufacture__date_shipment=date(2021, 1, 2))

        component = component_factory(
            is_reserve=True,
            is_stock=False,
            date_delivery=None,
            nomenclature=nomenclature,
        )
        form_data = {
            "component_type": component.component_type.pk,
            "is_stock": False,
            "count": 2,
            "date_delivery": date(2021, 1, 1),
        }
        url = reverse("component-create")
        response = operator_client.post(url, data=form_data)
        assert response.status_code == 302
        component.refresh_from_db()
        assert component.is_stock is False
        assert component.is_reserve is True
        assert component.date_delivery == date(2021, 1, 1)
        assert Component.objects.count() == 2
