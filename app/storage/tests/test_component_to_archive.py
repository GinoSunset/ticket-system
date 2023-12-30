import pytest
import pytest

from manufactures.models import Manufacture, Nomenclature
from additionally.models import Dictionary, DictionaryType
from storage.models import Component


@pytest.mark.django_db
def test_all_components_has_status_archive_after_status_to_shipment(
    nomenclature_factory,
):
    nomenclature = nomenclature_factory()
    nomenclature.status = nomenclature.Status.SHIPPED

    nomenclature.save()

    components = Component.objects.filter(nomenclature=nomenclature)
    assert all([component.is_archive for component in components])
