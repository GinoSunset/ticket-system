from django.db.models.signals import post_save
from django.dispatch import receiver

from manufactures.models import Manufacture
from storage.reserve import processing_reserved_component


@receiver(post_save, sender=Manufacture)
def create_user_report(sender, instance, created, **kwargs):
    if created:
        processing_reserved_component(instance)
