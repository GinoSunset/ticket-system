import pytest
from django.urls import reverse
from storage.models import Component


@pytest.mark.django_db
def test_add_component_to_stock_when_added_serial_number_by_form(
    nomenclature_factory, monkeypatch_delay_reserve_component_celery, operator_client
):
    nomenclature = nomenclature_factory()
    component = nomenclature.components.first()
    form_data = {
        "form-0-id": component.id,
        "form-0-serial_number": "2",
        "form-TOTAL_FORMS": 1,
        "form-INITIAL_FORMS": 1,
    }
    url = reverse(
        "add-serial-number",
        kwargs={"nomenclature_pk": nomenclature.pk, "pk": component.component_type.pk},
    )
    res = operator_client.post(url, form_data)
    assert res.status_code == 200
    component.refresh_from_db()
    assert component.serial_number == "2"
    assert component.is_phantom is False, "Компонент должен быть не на складе"


@pytest.mark.django_db
def tet_change_component_in_delivery_to_stock_and_free_this_component_in_delivery(
    nomenclature_factory, monkeypatch_delay_reserve_component_celery
):
    assert False


@pytest.mark.django_db
def test_change_status_in_stock_when_add_serial_number(
    nomenclature_factory, monkeypatch_delay_reserve_component_celery, operator_client
):
    nomenclature = nomenclature_factory()
    component = nomenclature.components.first()
    form_data = {
        "form-0-id": component.id,
        "form-0-serial_number": "2",
        "form-TOTAL_FORMS": 1,
        "form-INITIAL_FORMS": 1,
    }
    url = reverse(
        "add-serial-number",
        kwargs={"nomenclature_pk": nomenclature.pk, "pk": component.component_type.pk},
    )
    res = operator_client.post(url, form_data)
    assert res.status_code == 200
    component.refresh_from_db()
    assert component.serial_number == "2"
    assert component.is_stock is True, "Компонент должен быть на складе"


@pytest.mark.django_db
def test_after_change_status_to_ready_nomenclature_component_with_serial_number_save(
    nomenclature_factory, monkeypatch_delay_reserve_component_celery, operator_client
):
    nomenclature = nomenclature_factory()
    component = nomenclature.components.first()
    component.serial_number = "2"
    component.save()
    nomenclature.status = nomenclature.Status.READY
    nomenclature.save()
    component.refresh_from_db()
    assert Component.objects.filter(serial_number="2").exists()