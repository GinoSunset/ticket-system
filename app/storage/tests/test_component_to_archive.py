import pytest
import pytest

from manufactures.models import Manufacture, Nomenclature
from additionally.models import Dictionary, DictionaryType
from storage.models import Component


@pytest.mark.django_db
def test_all_components_has_status_archive_after_status_to_shipment(
    manufacture_factory, nomenclature_factory
):
    status_shipped = Dictionary.objects.get(
        code="shipped", type_dict=DictionaryType.objects.get(code="status_manufactory")
    )
    manufacture = manufacture_factory()
    nomenclature = nomenclature_factory(manufacture=manufacture)
    manufacture.status = status_shipped
    manufacture.save()

    components = Component.objects.filter(nomenclature=nomenclature)
    assert all([component.is_archive for component in components])
