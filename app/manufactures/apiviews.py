from rest_framework.generics import ListAPIView
from rest_framework_datatables.django_filters.backends import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.renderers import DatatablesRenderer
from .models import Manufacture
from .serializers import ManufactureSerializer
from .filters import ManufactureGlobalFilter


class ManufactureDataTableAPIView(ListAPIView):
    page_size = 10
    queryset = Manufacture.objects.all()
    serializer_class = ManufactureSerializer
    pagination_class = DatatablesPageNumberPagination
    filter_backends = (DatatablesFilterBackend,)
    filterset_class = ManufactureGlobalFilter
    ordering = ["-date_create"]