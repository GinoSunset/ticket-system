from django.urls import reverse
import pytest


@pytest.mark.django_db
def test_search_manufacture_by_component_serial_number(
    nomenclature_factory, monkeypatch_delay_reserve_component_celery, operator_client
):
    nomenclature = nomenclature_factory()
    component = nomenclature.component_set.first()
    component.serial_number = "123456789"
    component.save()
    response = operator_client.get(
        reverse("manufactures-list"), data={"serial_number": "123"}
    )
    assert response.status_code == 200
    assert response.data["count"] == 1
