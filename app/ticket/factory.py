import factory
from .models import Ticket, Comment
from users.factory import CustomerFactory


class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticket

    description = factory.Faker("text")
    customer = factory.SubFactory(CustomerFactory)
    sap_id = factory.Faker("ean")
    address = factory.Faker("address")


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    text = factory.Faker("text")
    ticket = factory.SubFactory(TicketFactory)
    user = factory.SubFactory(CustomerFactory)
