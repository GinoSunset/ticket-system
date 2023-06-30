import factory
from .models import Manufacture, Nomenclature, Client
from users.factory import OperatorFactory


class ClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Client

    name = factory.Faker("ean")
    comment = factory.Faker("ean")


class NomenclatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Nomenclature


class ManufactureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Manufacture

    operator = factory.SubFactory(OperatorFactory)
    client = factory.SubFactory(ClientFactory)
    comment = factory.Faker("text")

    @factory.post_generation
    def nomenclatures(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for nomenclature in extracted:
                self.nomenclatures.add(nomenclature)
