import factory
from .models import Notification


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification
