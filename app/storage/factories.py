import factory
from .models import Component, ComponentType, Delivery, TagComponent, Invoice, InvoiceAliasRelation, Alias


class ComponentTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComponentType

    name = factory.Faker("name")
    is_internal = factory.Faker("boolean")


class TagComponentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TagComponent

    name = factory.Faker("name")


class ComponentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Component

    component_type = factory.SubFactory(ComponentTypeFactory)
    is_reserve = factory.Faker("boolean")
    is_stock = factory.Faker("boolean")
    serial_number = factory.Faker("ean13")
    date_delivery = factory.Faker("date")

    @factory.post_generation
    def component_type_name(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.component_type.name = extracted
            self.component_type.save()


class DeliveryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Delivery

    date_delivery = factory.Faker("date")

class AliasFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Alias
    
    name = factory.Faker("text")
    component_type = factory.SubFactory(ComponentTypeFactory)

    

class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Invoice

    delivery = factory.SubFactory(DeliveryFactory)
    file_invoice = factory.django.FileField()


class InvoiceAliasRelationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InvoiceAliasRelation

    invoice = factory.SubFactory(InvoiceFactory)
    alias = factory.SubFactory(AliasFactory)
    