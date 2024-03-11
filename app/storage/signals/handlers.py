import logging
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from manufactures.models import Nomenclature
from storage.reserve import re_reserved_component_delivery, unreserve_components
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


@receiver(pre_delete, sender=Nomenclature)
def unreserve_components_before_delete(sender, instance, using, **kwargs):
    """
    Перед удалением номенклатуры, нужно очистить компоненты,
    фантомные удалить, у реальных снять бронь
    """
    logging.info(f"Delete {instance}. Start clean components")
    unreserve_components(instance)
