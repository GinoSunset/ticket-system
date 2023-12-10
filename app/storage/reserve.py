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
    try:
        # TODO: get type components from all options nomenclature (body, frame, etc.)
        type_component = ComponentType.objects.get(name=nomenclature.frame_type.name)
    except ComponentType.DoesNotExist:
        return None
    list_components_type = get_sub_component_from_component(type_component)
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
            date_delivery__gte=nomenclature.manufacture.date_shipment
        )
    else:
        q_conditions |= Q(date_delivery__isnull=False)
    component, created = Component.objects.filter(q_conditions).get_or_create(
        component_type=component_type,
        is_reserve=False,
        defaults={
            "nomenclature": nomenclature,
            "name": component_type.name,
            "is_reserve": True,
        },
    )
    if created:
        logging.info(f"Create component {component} to reserve")
        return
    logging.info(f"Update component {component} to reserve")
    component.nomenclature = nomenclature
    component.is_reserve = True
    component.save()
