import pytest

from storage.models import Component
from manufactures.models import Nomenclature, FrameTypeOption
from storage.facroties import ComponentFactory, ComponentTypeFactory


def create_components_rs_type():
    ComponentTypeFactory(name="РЧ", is_internal=True)


@pytest.mark.django_db
def test_has_needs_after_create_manufactory(manufacture_factory, nomenclature_factory):
    create_components_rs_type()
    manuf = manufacture_factory()
    nomenclatures = nomenclature_factory.create_batch(
        3, frame_type=FrameTypeOption.objects.get(name="РЧ"), manufacture=manuf
    )

    assert Component.objects.count() > 0
