from django_filters import filters
from django.db.models import Q
from rest_framework_datatables.django_filters.filterset import DatatablesFilterSet
from rest_framework_datatables.django_filters.filters import GlobalFilter
from .models import Manufacture


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


class ManufactureGlobalFilter(DatatablesFilterSet):
    id = GlobalCharFilter(lookup_expr="icontains")
    status = GlobalCharFilter(field_name="status__description", lookup_expr="icontains")
    # client = GlobalFullNameAndCompanyFilter(lookup_expr="icontains")
    comment = GlobalCharFilter(lookup_expr="icontains")
    ticket = GlobalCharFilter(field_name="ticket__pk", lookup_expr="icontains")

    class Meta:
        model = Manufacture
        fields = (
            "id",
            "status",
            "client",
            "comment",
            "ticket",
        )
