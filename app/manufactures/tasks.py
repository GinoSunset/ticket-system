from ticsys import celery_app
import logging
from manufactures.models import Nomenclature
from storage.reserve import (
    processing_reserved_component,
    remove_phantom_component_on_nomenclature,
    unreserve_components,
    components_from_nomenclature_to_archive,
)


@celery_app.task
def reservation_component_from_nomenclature(id_nomenclature, created):
    logging.debug("Start reservation")
    Nomenclature.objects.filter(pk=id_nomenclature).update(is_reserving=True)
    try:
        result = reserve_components(id_nomenclature, created)
    finally:
        Nomenclature.objects.filter(pk=id_nomenclature).update(is_reserving=False)
    logging.debug(f"Stop reservation for {id_nomenclature}")
    return result


def reserve_components(id_nomenclature, created):
    nomenclature: Nomenclature = Nomenclature.objects.get(pk=id_nomenclature)
    if created and nomenclature.manufacture:
        processing_reserved_component(nomenclature)
        return
    if not created and nomenclature.manufacture:
        if nomenclature.status == Nomenclature.Status.CANCELED:
            unreserve_components(nomenclature)
            return
        remove_phantom_component_on_nomenclature(nomenclature)
        processing_reserved_component(nomenclature)
        if nomenclature.status == Nomenclature.Status.SHIPPED:
            components_from_nomenclature_to_archive(nomenclature)
