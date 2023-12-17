import pytest
from datetime import date
from django.urls import reverse
from django.test import Client
from storage.models import Component

from storage.forms import ComponentForm
from storage.views import ComponentCreateView


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
class TestComponentCreateView:
    def test_form_valid_with_non_stock_component(
        self, client, component_factory, manufacture_factory, nomenclature_factory
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
            "serial_number": "ABC123",
            "date_delivery": date(2021, 1, 1),
        }
        url = reverse("component-create")
        response = client.post(url, data=form_data)
        assert response.status_code == 302
        needed_component.refresh_from_db()
        assert needed_component.is_stock is False
        assert needed_component.serial_number == "ABC123"
        assert needed_component.date_delivery == date(2021, 1, 1)

    def test_form_valid_with_stock_component(self, client, component_factory):
        component = component_factory(
            is_reserve=True, is_stock=False, date_delivery=None
        )
        form_data = {
            "component_type": component.component_type.pk,
            "is_stock": True,
        }
        url = reverse("component-create")
        response = client.post(url, data=form_data)
        assert response.status_code == 302
        component.refresh_from_db()
        assert component.is_stock is True

    def test_form_valid_create_new_stock_component(self, client, component_type):
        form_data = {
            "component_type": component_type.pk,
            "is_stock": True,
        }
        url = reverse("component-create")
        response = client.post(url, data=form_data)
        assert response.status_code == 302
        component = Component.objects.get(pk=1)
        assert component.is_stock is True
