import factory
from .models import Manufacture, Nomenclature, Client
from users.factory import OperatorFactory
from additionally.models import Dictionary


class ClientManufFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Client

    name = factory.Faker("ean")
    comment = factory.Faker("ean")


class NomenclatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Nomenclature

    comment = factory.Faker("text")


class ManufactureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Manufacture

    operator = factory.SubFactory(OperatorFactory)
    client = factory.SubFactory(ClientManufFactory)
    comment = factory.Faker("text")
    
    @factory.post_generation
    def status(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.status = extracted
            self.save()
        else:
            self.status = Dictionary.objects.get(code="new_manufacture_task")
            self.save()
    

    @factory.post_generation
    def nomenclatures(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for nomenclature in extracted:
                self.nomenclatures.add(nomenclature)
