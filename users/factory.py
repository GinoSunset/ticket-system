import factory
from .models import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "User%03d" % n)
    email = factory.Sequence(lambda n: "User%03d@mail.com" % n)
