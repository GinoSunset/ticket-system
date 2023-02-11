import factory
from .models import Ticket
from users.factory import CustomerFactory


class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticket

    description = factory.Faker("text")
    customer = factory.SubFactory(CustomerFactory)
