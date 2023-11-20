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
