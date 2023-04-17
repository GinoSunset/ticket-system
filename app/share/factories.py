import factory
from .models import Share

from ticket.factory import TicketFactory
from users.factory import OperatorFactory


class ShareFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Share

    ticket = factory.SubFactory(TicketFactory)
    creator = factory.SubFactory(OperatorFactory)
