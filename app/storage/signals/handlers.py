from django.dispatch import receiver
from django.db.models.signals import post_save

from manufactures.models import Nomenclature
from storage.reserve import (
    processing_reserved_component,
    components_from_nomenclature_to_archive,
)


@receiver(post_save, sender=Nomenclature)
def reserve_component_on_nomenclature(sender, instance, created, **kwargs):
    if created and instance.manufacture:
        processing_reserved_component(instance)
        return
    if not created and instance.manufacture:
        if instance.status == Nomenclature.Status.SHIPPED:
            components_from_nomenclature_to_archive(instance)
