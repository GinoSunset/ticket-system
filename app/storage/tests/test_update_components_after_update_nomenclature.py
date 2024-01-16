import pytest
import pytest

from manufactures.models import Manufacture, Nomenclature
from additionally.models import Dictionary, DictionaryType
from storage.models import Component, ComponentType


@pytest.mark.django_db
def test_all_components_has_status_archive_after_status_to_shipment(
    nomenclature_factory,
):
    nomenclature = nomenclature_factory()
    nomenclature.status = nomenclature.Status.SHIPPED

    nomenclature.save()

    components = Component.objects.filter(nomenclature=nomenclature)
    assert all([component.is_archive for component in components])


@pytest.mark.django_db
def test_change_update_composenent_after_up_count_nomenclature_components(
    nomenclature_factory
):
    nomenclature = nomenclature_factory(rx_count=1)
    componet_typeAM_RX = ComponentType.objects.get(pk=1)
    assert Component.objects.filter(nomenclature=nomenclature, component_type=componet_typeAM_RX).count() == 1

    nomenclature.rx_count = 2
    nomenclature.save()

    assert Component.objects.filter(nomenclature=nomenclature, component_type=componet_typeAM_RX).count() == 2

    