import django_filters
from .models import Manufacture


class ManufactureFilter(django_filters.FilterSet):
    client = django_filters.CharFilter(lookup_expr="icontains")
    comment = django_filters.CharFilter(lookup_expr="icontains")
    date_create = django_filters.DateFilter(lookup_expr="gte")
    date_shipment = django_filters.DateFilter(lookup_expr="lte")
    pk = django_filters.NumberFilter(lookup_expr="exact")

    class Meta:
        model = Manufacture
        fields = ["pk", "client", "comment", "date_create", "date_shipment", "status"]
