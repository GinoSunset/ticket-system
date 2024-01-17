from django import template
from django.db.models import Q

from storage.models import ComponentType, Component

register = template.Library()


@register.filter
def get_value_progress(component):
    in_reserve_not_in_stock_not_in_delivery = (
        Component.active_components.filter(
            component_type_id=component["component_type"]
        )
        .filter(
            is_reserve=True,
            is_stock=False,
            date_delivery__isnull=True,
        )
        .count()
    )
    in_reserve_not_in_stock_in_delivery = (
        Component.active_components.filter(
            component_type_id=component["component_type"]
        )
        .filter(
            is_reserve=True,
            is_stock=False,
            date_delivery__isnull=False,
        )
        .count()
    )
    in_delivery = (
        Component.active_components.filter(
            component_type_id=component["component_type"]
        )
        .filter(
            is_reserve=False,
            is_stock=False,
            date_delivery__isnull=False,
        )
        .count()
    )
    in_reserve_in_stock_not_in_delivery = (
        Component.active_components.filter(
            component_type_id=component["component_type"]
        )
        .filter(
            Q(date_delivery__isnull=True) | Q(date_delivery__isnull=False),
            is_reserve=True,
            is_stock=True,
        )
        .count()
    )
    in_stock = (
        Component.active_components.filter(
            component_type_id=component["component_type"]
        )
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
