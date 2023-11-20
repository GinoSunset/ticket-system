import pytest

from storage.models import Component
from manufactures.models import Nomenclature, FrameTypeOption
from storage.models import ComponentType
from storage.facroties import ComponentFactory, ComponentTypeFactory


def create_components_rs_type(
    inner_component_type: ComponentType | None = None,
) -> ComponentType:
    component = ComponentTypeFactory(name="РЧ", is_internal=True)
    if inner_component_type:
        component.sub_component_type = inner_component_type
        component.save()
    return component


@pytest.mark.django_db
def test_has_needs_after_create_manufactory(manufacture_factory, nomenclature_factory):
    create_components_rs_type()
    manuf = manufacture_factory()
    nomenclatures = nomenclature_factory.create_batch(
        3, frame_type=FrameTypeOption.objects.get(name="РЧ"), manufacture=manuf
    )

    assert Component.objects.count() > 0


@pytest.mark.django_db
def test_create_components_with_type_with_subcomponent(nomenclature_factory):
    name_sub_component = "Чип РЧ"
    inner_component_type = ComponentTypeFactory(name=name_sub_component)
    component = create_components_rs_type(inner_component_type=inner_component_type)

    nomenclature_factory(frame_type=FrameTypeOption.objects.get(name="РЧ"))

    assert Component.objects.count() == 2
    assert Component.objects.filter(name=name_sub_component).exists()
