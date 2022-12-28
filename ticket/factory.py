import factory
from .models import Ticket


class TicketFactory(factory.Factory):
    class Meta:
        model = Ticket
