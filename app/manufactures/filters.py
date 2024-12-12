from django_filters import filters
from django.db.models import Q
from rest_framework_datatables.django_filters.filterset import DatatablesFilterSet
from rest_framework_datatables.django_filters.filters import GlobalFilter
from .models import Manufacture

class GlobalCharFilter(GlobalFilter, filters.CharFilter):
    pass



class GlobalComponentSerialNumber(GlobalFilter, filters.CharFilter):
    def global_q(self):
        ret = super().global_q()
        ret |= Q(
            **{
                f"nomenclatures__components__serial_number__icontains": self.global_search_value
            }
        )
        return ret


class ManufactureGlobalFilter(DatatablesFilterSet):
    pk = GlobalCharFilter(lookup_expr="icontains")
    status = GlobalCharFilter(field_name="status__description", lookup_expr="icontains")
    client = GlobalCharFilter(field_name="client__name", lookup_expr="icontains")
    comment = GlobalCharFilter(lookup_expr="icontains")
    ticket = GlobalCharFilter(field_name="ticket__pk", lookup_expr="icontains")
    serial_number_component = GlobalComponentSerialNumber()

    class Meta:
        model = Manufacture
        fields = (
            "pk",
            "status",
            "client",
            "comment",
            "ticket",
            "serial_number_component",
        )

    def filter_queryset(self, queryset):
        print("Фильтруем данные:", self.data)
        queryset = super().filter_queryset(queryset)
        print("Отфильтрованный результат:", queryset.query)
        return queryset