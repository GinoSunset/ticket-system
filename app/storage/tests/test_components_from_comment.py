import pytest

from storage.models import Component


@pytest.mark.django_db
def test_reserve_component_from_comment(nomenclature_factory, component_factory):
    component_factory(nomenclature=None, component_type__name="деатоватор")
    nomenclature_factory(comment="необходимо {деатоватор 4 шт}")
    assert Component.objects.filter(component_type__name="деатоватор").count() == 4
