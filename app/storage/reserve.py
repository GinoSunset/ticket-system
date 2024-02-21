from django.db.models import Q
from manufactures.models import Manufacture, Nomenclature
from django.db.transaction import atomic
from .models import Component, ComponentType, SubComponentTypeRelation
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
            type_component = ComponentType.objects.get(name__icontains=component)
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
            count_sub_components = SubComponentTypeRelation.objects.get(
                parent_component_type=component_type,
                sub_component_type=sub_component_type,
            ).count_sub_components
            for _ in range(count_sub_components):
                components_type.extend(
                    get_sub_component_from_component(sub_component_type)
                )
    return components_type


@atomic
def reserve_component(component_type: ComponentType, nomenclature: Nomenclature):
    q_conditions = Q(is_stock=True)
    if nomenclature.manufacture and nomenclature.manufacture.date_shipment:
        q_conditions |= Q(date_delivery__isnull=False) & Q(
            date_delivery__lte=nomenclature.manufacture.date_shipment
        )
    else:
        q_conditions |= Q(date_delivery__isnull=False)
    components = Component.objects.select_for_update().filter(
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


def components_from_nomenclature_to_archive(nomenclature: Nomenclature):
    Component.objects.filter(nomenclature=nomenclature).update(is_archive=True)
    logging.info(f"All components with nomenclature {nomenclature} are archived")


def unreserve_components(nomenclature: Nomenclature):
    count_remove = Component.objects.filter(
        nomenclature=nomenclature,
        is_stock=False,
        is_reserve=True,
        date_delivery__isnull=True,
    ).delete()
    count_update = Component.objects.filter(
        nomenclature=nomenclature, is_reserve=True
    ).update(is_reserve=False, nomenclature=None)
    logging.info(
        f"Remove {count_remove} component. Unreserve {count_update} component for Nomenclature {nomenclature} "
    )


def re_reserved_component_delivery(component: Component):
    """
    Проверяет правильность резервирования, и если дата доставки после обновления
    доставки выше даты отгрузки номенклатуры, то снимаем резерв с товара и ищется новый резерв
    """
    nomenclature_from_component = component.nomenclature
    if not nomenclature_from_component:
        return
    if nomenclature_from_component.manufacture.date_shipment is None:
        return
    if (
        not nomenclature_from_component.manufacture.date_shipment
        < component.date_delivery
    ):
        return

    component.is_reserve = False
    component.nomenclature = None
    component.save()
    reserve_component(
        component_type=component.component_type,
        nomenclature=nomenclature_from_component,
    )
