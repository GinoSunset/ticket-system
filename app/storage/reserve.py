from manufactures.models import Manufacture, Nomenclature
from .models import Component, ComponentType


def processing_reserved_component(nomenclature: Nomenclature):
    components_type = get_components_type_from_nomenclature(nomenclature)
    if not components_type:
        return
    for component_type in components_type:
        reserve_component(component_type, nomenclature)


def get_components_type_from_nomenclature(
    nomenclature: Nomenclature,
) -> list[ComponentType] | None:
    try:
        type_component = ComponentType.objects.get(name=nomenclature.frame_type.name)
    except ComponentType.DoesNotExist:
        return None
    list_components_type = get_sub_component_from_component(type_component)
    return list_components_type


def get_sub_component_from_component(
    component_type: ComponentType,
) -> list[ComponentType]:
    components_type = [component_type]
    if component_type.sub_component_type:
        components_type.extend(
            get_sub_component_from_component(component_type.sub_component_type)
        )
    return components_type


def reserve_component(component_type: ComponentType, nomenclature: Nomenclature):
    Component.objects.create(
        component_type=component_type,
        is_reserve=True,
        nomenclature=nomenclature,
        name=component_type.name,
    )
