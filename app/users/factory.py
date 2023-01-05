import factory
from .models import User, Customer, CustomerProfile, Operator


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "User%03d" % n)
    email = factory.Sequence(lambda n: "User%03d@mail.com" % n)


class CustomerProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomerProfile


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    username = factory.Sequence(lambda n: "customer%03d" % n)
    email = factory.Sequence(lambda n: "customer%03d@mail.com" % n)


class OperatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Operator

    username = factory.Sequence(lambda n: "operator%03d" % n)
    email = factory.Sequence(lambda n: "operator%03d@mail.com" % n)
