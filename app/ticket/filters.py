from django_filters import filters
from django.db.models import Q
from rest_framework_datatables.django_filters.filterset import DatatablesFilterSet
from rest_framework_datatables.django_filters.filters import GlobalFilter
from .models import Ticket


class GlobalCharFilter(GlobalFilter, filters.CharFilter):
    pass


class TicketGlobalFilter(DatatablesFilterSet):
    city = GlobalCharFilter(lookup_expr="icontains")
    id = GlobalCharFilter(lookup_expr="icontains")
    # date_create = GlobalCharFilter(lookup_expr="icontains")
    sap_id = GlobalCharFilter(lookup_expr="icontains")
    type_ticket = GlobalCharFilter(
        field_name="type_ticket__description", lookup_expr="icontains"
    )
    customer = GlobalCharFilter(field_name="full_name", method="search_by_full_name")
    responsible = GlobalCharFilter(field_name="full_name", method="search_by_full_name")
    contractor = GlobalCharFilter(field_name="full_name", method="search_by_full_name")
    # planned_execution_date = filters.DateTimeFilter()
    status = GlobalCharFilter(field_name="status__description", lookup_expr="icontains")
    address = GlobalCharFilter(lookup_expr="icontains")
    shop_id = GlobalCharFilter(lookup_expr="icontains")

    def search_by_full_name(self, qs, name, value):
        for term in value.split():
            qs = qs.filter(
                Q(firs_name__icontains=term)
                | Q(last_name__icontains=term)
                | Q(username__icontains=term)
            )
        return qs

    class Meta:
        model = Ticket
        fields = (
            "city",
            "id",
            "sap_id",
            "type_ticket",
            "customer",
            "responsible",
            "contractor",
            "status",
            "address",
            "shop_id",
        )
