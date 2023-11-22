import factory
from .models import Component, ComponentType


class ComponentTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComponentType

    name = factory.Faker("name")
    is_internal = factory.Faker("boolean")


class ComponentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Component

    name = factory.Faker("name")
    component_type = factory.SubFactory(ComponentTypeFactory)
    is_reserve = factory.Faker("boolean")
    is_stock = factory.Faker("boolean")
    serial_number = factory.Faker("ean13")
    nomenclature = factory.SubFactory("manufactures.factories.NomenclatureFactory")
    date_delivery = factory.Faker("date")

    @factory.post_generation
    def component_type_name(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.component_type.name = extracted
            self.component_type.save()
