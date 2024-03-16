from django import template
from django.db.models import Q

from storage.models import ComponentType, Component

register = template.Library()


def filter_components_by_type(component, nomenclature=None):
    if nomenclature:
        return Component.active_components.filter(
            component_type_id=component["component_type"], nomenclature=nomenclature
        )
    return Component.active_components.filter(
        component_type_id=component["component_type"]
    )


@register.filter
def get_value_progress(component, nomenclature=False):
    in_reserve_not_in_stock_not_in_delivery = (
        filter_components_by_type(component, nomenclature)
        .filter(is_reserve=True, is_stock=False, date_delivery__isnull=True)
        .count()
    )

    in_reserve_not_in_stock_in_delivery = (
        filter_components_by_type(component, nomenclature)
        .filter(is_reserve=True, is_stock=False, date_delivery__isnull=False)
        .count()
    )

    in_delivery = (
        filter_components_by_type(component, nomenclature)
        .filter(is_reserve=False, is_stock=False, date_delivery__isnull=False)
        .count()
    )

    in_reserve_in_stock_not_in_delivery = (
        filter_components_by_type(component, nomenclature)
        .filter(
            Q(date_delivery__isnull=True) | Q(date_delivery__isnull=False),
            is_reserve=True,
            is_stock=True,
        )
        .count()
    )

    in_stock = (
        filter_components_by_type(component, nomenclature)
        .filter(
            Q(date_delivery__isnull=True) | Q(date_delivery__isnull=False),
            is_reserve=False,
            is_stock=True,
        )
        .count()
    )

    return ",".join(
        [
            str(in_reserve_not_in_stock_not_in_delivery),
            str(in_reserve_not_in_stock_in_delivery),
            str(in_delivery),
            str(in_reserve_in_stock_not_in_delivery),
            str(in_stock),
        ]
    )
