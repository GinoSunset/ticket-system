from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .models import Manufacture
from .serializers import ManufactureSerializer
from .filters import ManufactureFilter


class ManufacturePagination(PageNumberPagination):
    page_size_query_param = "length"  # DataTables использует параметр `length`


class ManufactureViewSet(ModelViewSet):
    queryset = Manufacture.objects.all()
    serializer_class = ManufactureSerializer
    pagination_class = ManufacturePagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ManufactureFilter
    ordering_fields = ["pk", "date_create", "date_shipment", "count"]
    search_fields = ["client", "comment"]
