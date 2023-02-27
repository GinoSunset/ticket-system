import factory
from .models import Report, Act

from users.factory import UserFactory


class ReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Report

    creator = factory.SubFactory(UserFactory)
    start_date = factory.Faker("date_between", start_date="-30d", end_date="-1d")
    end_date = factory.Faker("date_between", start_date="+1d", end_date="+30d")


class ActFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Act

    ticket = factory.SubFactory("ticket.factory.TicketFactory")
