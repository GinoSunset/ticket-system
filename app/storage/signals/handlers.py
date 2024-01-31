from django.dispatch import receiver
from django.db.models.signals import post_save

from manufactures.models import Nomenclature
from storage.reserve import (
    processing_reserved_component,
    components_from_nomenclature_to_archive,
    unreserve_components,
    re_reserved_component_delivery,
)
from storage.models import Delivery


@receiver(post_save, sender=Nomenclature)
def reserve_component_on_nomenclature(sender, instance, created, **kwargs):
    if created and instance.manufacture:
        processing_reserved_component(instance)
        return
    if not created and instance.manufacture:
        unreserve_components(instance)
        processing_reserved_component(instance)
        if instance.status == Nomenclature.Status.SHIPPED:
            components_from_nomenclature_to_archive(instance)


@receiver(post_save, sender=Delivery)
def change_data_on_component(sender, instance, created, **kwargs):
    if not created:
        components = instance.component_set.all()
        components.update(date_delivery=instance.date_delivery)
        for component in components:
            re_reserved_component_delivery(component)
