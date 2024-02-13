from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_datatables.django_filters.backends import DatatablesFilterBackend
from .models import Ticket
from .serializers import TicketSerializer
from .filters import TicketGlobalFilter


class TicketsList(generics.ListAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DatatablesFilterBackend,)
    filterset_class = TicketGlobalFilter
