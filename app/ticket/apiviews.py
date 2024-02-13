from typing import Any, Union

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_datatables.django_filters.backends import DatatablesFilterBackend
from django.db.models import QuerySet
from .models import Ticket
from .serializers import TicketSerializer
from .filters import TicketGlobalFilter
from users.models import Operator, Customer, User, Contractor


class TicketsList(generics.ListAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DatatablesFilterBackend,)
    filterset_class = TicketGlobalFilter

    # TODO: test os not created
    def get_queryset(self) -> QuerySet[Ticket]:

        queryset = super().get_queryset()
        user: Union[Customer, Contractor, Operator] = self.request.user.get_role_user()
        if user.is_staff:
            return queryset
        filter_from_user: dict = user.get_ticket_filter() or {}
        return queryset.filter(**filter_from_user)
