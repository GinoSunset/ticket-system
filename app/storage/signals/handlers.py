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
from manufactures.tasks import reservation_component_from_nomenclature


@receiver(post_save, sender=Nomenclature)
def reserve_component_on_nomenclature(sender, instance, created, **kwargs):
    reservation_component_from_nomenclature.delay(instance.pk, created)


@receiver(post_save, sender=Delivery)
def change_data_on_component(sender, instance, created, **kwargs):
    if not created:
        components = instance.component_set.all()
        components.update(date_delivery=instance.date_delivery)
        for component in components:
            re_reserved_component_delivery(component)
