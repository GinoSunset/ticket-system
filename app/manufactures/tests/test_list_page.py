from django.urls import reverse
import pytest

from manufactures.filters import ManufactureGlobalFilter


@pytest.mark.django_db
def test_serial_number_filter(
    nomenclature_factory, monkeypatch_delay_reserve_component_celery, client
):
    nomenclature = nomenclature_factory()
    component = nomenclature.components.first()
    component.serial_number = "SN001"
    component.save()
    manufacture = nomenclature.manufacture

    data_search = {
        "format": "datatables",
        "draw": 1,
        "columns[0][data]": "pk",
        "columns[0][name]": "",
        "columns[0][searchable]": "true",
        "columns[0][orderable]": "true",
        "columns[0][search][value]": "",
        "columns[0][search][regex]": "false",
        "columns[1][data]": "date_create",
        "columns[1][name]": "",
        "columns[1][searchable]": "true",
        "columns[1][orderable]": "true",
        "columns[1][search][value]": "",
        "columns[1][search][regex]": "false",
        "columns[2][data]": "client",
        "columns[2][name]": "",
        "columns[2][searchable]": "true",
        "columns[2][orderable]": "true",
        "columns[2][search][value]": "",
        "columns[2][search][regex]": "false",
        "columns[3][data]": "date_shipment",
        "columns[3][name]": "",
        "columns[3][searchable]": "true",
        "columns[3][orderable]": "true",
        "columns[3][search][value]": "",
        "columns[3][search][regex]": "false",
        "columns[4][data]": "count",
        "columns[4][name]": "",
        "columns[4][searchable]": "true",
        "columns[4][orderable]": "false",
        "columns[4][search][value]": "",
        "columns[4][search][regex]": "false",
        "columns[5][data]": "branding",
        "columns[5][name]": "",
        "columns[5][searchable]": "true",
        "columns[5][orderable]": "false",
        "columns[5][search][value]": "",
        "columns[5][search][regex]": "false",
        "columns[6][data]": "status",
        "columns[6][name]": "",
        "columns[6][searchable]": "true",
        "columns[6][orderable]": "false",
        "columns[6][search][value]": "",
        "columns[6][search][regex]": "false",
        "columns[7][data]": "comment",
        "columns[7][name]": "",
        "columns[7][searchable]": "true",
        "columns[7][orderable]": "false",
        "columns[7][search][value]": "",
        "columns[7][search][regex]": "false",
        "columns[8][data]": "actions",
        "columns[8][name]": "",
        "columns[8][searchable]": "true",
        "columns[8][orderable]": "false",
        "columns[8][search][value]": "",
        "columns[8][search][regex]": "false",
        "columns[9][data]": "serial_number",
        "columns[9][name]": "serial_number",
        "columns[9][searchable]": "true",
        "columns[9][orderable]": "true",
        "columns[9][search][value]": "",
        "columns[9][search][regex]": "false",
        "search[value]": "SN001",
    }
    res = client.get(reverse("api-manufactures"), data=data_search)

    data = res.json()
    assert manufacture.pk == data["data"][0]["pk"]
