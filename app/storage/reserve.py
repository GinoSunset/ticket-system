from django.db.models import Q
from manufactures.models import Manufacture, Nomenclature
from ticket.models import Ticket

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
            type_component = ComponentType.objects.get(name__iexact=component)
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


def reserve_component(component_type: ComponentType, obj: Nomenclature | Ticket):
    match obj:
        case Nomenclature():
            reserve_component_nomenclature(component_type, obj)
        case Ticket():
            reserve_component_ticket(component_type, obj)


@atomic
def reserve_component_ticket(component_type: ComponentType, ticket: Ticket):
    q_conditions = Q(is_stock=True)
    components = Component.objects.select_for_update().filter(
        q_conditions, component_type=component_type, is_reserve=False
    )
    if components.exists():
        component = components.first()
        logging.info(f"{component}  reserved by {ticket}")
        component.ticket = ticket
        component.is_reserve = True
        component.save()
        return

    component = Component.objects.create(
        component_type=component_type,
        ticket=ticket,
        is_reserve=True,
    )
    logging.info(f"Create {component} for {ticket}")


@atomic
def reserve_component_nomenclature(
    component_type: ComponentType, nomenclature: Nomenclature
):
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
        logging.info(f"{component} reserve by {nomenclature}")
        component.nomenclature = nomenclature
        component.is_reserve = True
        component.save()
        return

    component = Component.objects.create(
        component_type=component_type,
        nomenclature=nomenclature,
        is_reserve=True,
    )
    logging.info(f"Create component {component} to reserve for {nomenclature}")


def components_from_tickets_to_archive(ticket: Ticket):
    count = Component.objects.filter(ticket=ticket).update(is_archive=True)
    logging.info(f"All {count} components with ticket {ticket} are archived")


def components_from_nomenclature_to_archive(nomenclature: Nomenclature):
    count = Component.objects.filter(nomenclature=nomenclature).update(is_archive=True)
    logging.info(
        f"All {count} components with nomenclature {nomenclature} are archived"
    )


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


def re_reserver_components_in_stock_to_phantoms():
    """
    Изменить резерв с компонентов фантомных на реальные компоненты на складе
    """
    component_types = get_component_type_in_stock_and_has_phantoms()
    for component_type in component_types:
        re_reserve_stock_component(component_type)


def re_reserve_stock_component(component_type: ComponentType):
    free_components = Component.active_components.filter(
        is_stock=True, is_reserve=False, component_type=component_type
    )
    components_phantom = Component.phantom_components.filter(
        component_type=component_type, phantom=True, nomenclature__isnull=False
    ).order_by("nomenclature__manufacture__date_shipment")

    for free_comp, phantom_comp in zip(free_components, components_phantom):
        with atomic():
            free_comp.is_reserve = True
            free_comp.nomenclature = phantom_comp.nomenclature
            free_comp.save()
            phantom_comp.delete()
            logging.info(
                f"{free_comp} will be reserve to {free_comp.nomenclature} by re_reserve_stock_component"
            )


def get_component_type_in_stock_and_has_phantoms():
    result = []
    for ct in ComponentType.objects.all():
        if (
            Component.active_components.filter(
                is_stock=True, is_reserve=False, component_type=ct
            ).exists()
            and Component.phantom_components.filter(
                phantom=True, component_type=ct, nomenclature__isnull=False
            ).exists()
        ):

            result.append(ct)

    return result
