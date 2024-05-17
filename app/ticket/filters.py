from django_filters import filters
from django.db.models import Q
from rest_framework_datatables.django_filters.filterset import DatatablesFilterSet
from rest_framework_datatables.django_filters.filters import GlobalFilter
from .models import Ticket


class GlobalCharFilter(GlobalFilter, filters.CharFilter):
    pass


class GlobalFullNameFilter(GlobalFilter, filters.CharFilter):

    def global_q(self):
        """Return a Q-Object for the global search for this column"""
        ret = Q()
        if self.global_search_value:
            for term in self.global_search_value.split(" "):
                ret |= (
                    Q(
                        **{
                            f"{self.field_name}__first_name__{self.global_lookup_expr}": term
                        }
                    )
                    | Q(
                        **{
                            f"{self.field_name}__last_name__{self.global_lookup_expr}": term
                        }
                    )
                    | Q(
                        **{
                            f"{self.field_name}__username__{self.global_lookup_expr}": term
                        }
                    )
                )
        return ret


class GlobalFullNameAndCompanyFilter(GlobalFullNameFilter):

    def global_q(self):
        ret = super().global_q()
        ret |= Q(
            **{
                f"{self.field_name}__profile__company__{self.global_lookup_expr}": self.global_search_value
            }
        )
        return ret


class TicketGlobalFilter(DatatablesFilterSet):
    city = GlobalCharFilter(lookup_expr="icontains")
    id = GlobalCharFilter(lookup_expr="icontains")
    # date_create = GlobalCharFilter(lookup_expr="icontains")
    sap_id = GlobalCharFilter(lookup_expr="icontains")
    type_ticket = GlobalCharFilter(
        field_name="type_ticket__description", lookup_expr="icontains"
    )
    customer = GlobalFullNameAndCompanyFilter(lookup_expr="icontains")
    responsible = GlobalFullNameFilter(lookup_expr="icontains")
    contractor = GlobalFullNameAndCompanyFilter(lookup_expr="icontains")
    # planned_execution_date = filters.DateTimeFilter()
    status = GlobalCharFilter(field_name="status__description", lookup_expr="icontains")
    address = GlobalCharFilter(lookup_expr="icontains")
    shop_id = GlobalCharFilter(lookup_expr="icontains")

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
