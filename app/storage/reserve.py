from manufactures.models import Manufacture, Nomenclature
from .models import Component, ComponentType


def processing_reserved_component(manufacture: Manufacture):
    for nomenclature in manufacture.nomenclatures.all():
        components_type = get_components_type_from_nomenclature(nomenclature)
        if not components_type:
            continue
        for component_type in components_type:
            reserve_component(component_type, manufacture)


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


def reserve_component(component_type: ComponentType, manufacture):
    Component.objects.create(
        component_type=component_type, is_reserve=True, manufacture=manufacture
    )
