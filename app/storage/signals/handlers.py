from django.dispatch import receiver
from django.db.models.signals import post_save

from manufactures.models import Nomenclature
from storage.reserve import processing_reserved_component


@receiver(post_save, sender=Nomenclature)
def create_user_report(sender, instance, created, **kwargs):
    if created and instance.manufacture:
        processing_reserved_component(instance)
