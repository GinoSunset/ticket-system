import pytest

from storage.models import Component
from manufactures.models import Nomenclature, FrameTypeOption


@pytest.mark.django_db
def test_has_needs_after_create_manufactory(manufacture_factory, nomenclature_factory):
    nomenclatures = nomenclature_factory.create_batch(
        3, frame_type=FrameTypeOption.objects.get(name="РЧ")
    )

    manuf = manufacture_factory(nomenclatures=nomenclatures)

    assert Component.objects.count() > 0
