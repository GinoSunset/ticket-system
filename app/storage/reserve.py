from django.db.models import Q
from manufactures.models import Manufacture, Nomenclature
from .models import Component, ComponentType
import logging


def processing_reserved_component(nomenclature: Nomenclature):
    components_type = get_components_type_from_nomenclature(nomenclature)
    if not components_type:
        return
    for component_type in components_type:
        reserve_component(component_type, nomenclature)


def get_components_type_from_nomenclature(
    nomenclature: Nomenclature,
) -> list[ComponentType] | None:
    components = nomenclature.get_components()
    list_components_type = []
    for component in components:
        try:
            type_component = ComponentType.objects.get(name=component)
        except ComponentType.DoesNotExist:
            continue
        list_components_type.extend(get_sub_component_from_component(type_component))
    return list_components_type


def get_sub_component_from_component(
    component_type: ComponentType,
) -> list[ComponentType]:
    components_type = [component_type]
    if sub_components_type := component_type.sub_components_type.all():
        for sub_component_type in sub_components_type:
            components_type.extend(get_sub_component_from_component(sub_component_type))
    return components_type


def reserve_component(component_type: ComponentType, nomenclature: Nomenclature):
    q_conditions = Q(is_stock=True)
    if nomenclature.manufacture and nomenclature.manufacture.date_shipment:
        q_conditions |= Q(date_delivery__isnull=False) & Q(
            date_delivery__lte=nomenclature.manufacture.date_shipment
        )
    else:
        q_conditions |= Q(date_delivery__isnull=False)
    components = Component.objects.filter(
        q_conditions, component_type=component_type, is_reserve=False
    )
    if components.exists():
        component = components.first()
        logging.info(f"Update component {component} to reserve")
        component.nomenclature = nomenclature
        component.is_reserve = True
        component.save()
        return

    component = Component.objects.create(
        component_type=component_type,
        nomenclature=nomenclature,
        is_reserve=True,
    )
    logging.info(f"Create component {component} to reserve")
