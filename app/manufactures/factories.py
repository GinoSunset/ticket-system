import factory
from .models import Manufacture, Nomenclature, Client
from users.factory import OperatorFactory
from additionally.models import Dictionary


class ClientManufFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Client

    name = factory.Faker("ean")
    comment = factory.Faker("ean")


class ManufactureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Manufacture

    operator = factory.SubFactory(OperatorFactory)
    client = factory.SubFactory(ClientManufFactory)
    comment = factory.Faker("text")


class NomenclatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Nomenclature

    comment = factory.Faker("text")
    manufacture = factory.SubFactory(ManufactureFactory)
