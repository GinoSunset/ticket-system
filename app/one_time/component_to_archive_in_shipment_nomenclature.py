"""
script send to archive component who has nomenclature has status shipment
"""

import os
import sys
import django
import logging


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ticsys.settings")
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
django.setup()


from manufactures.models import Manufacture, Nomenclature
from additionally.models import Dictionary
from storage.reserve import components_from_nomenclature_to_archive

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def components_to_archive():
    manufactures = get_shipped_manufacture()
    for manufacture in manufactures:
        for nomenclature in manufacture.nomenclatures.all():
            if nomenclature.status == Nomenclature.Status.SHIPPED:
                components_from_nomenclature_to_archive(nomenclature)
            nomenclature.status = Nomenclature.Status.SHIPPED
            nomenclature.save()


def get_shipped_manufacture():
    status_shipped = Dictionary.objects.get(code="shipped")
    manufactures = Manufacture.objects.filter(status=status_shipped)
    return manufactures


if __name__ == "__main__":
    logging.info("Starting script for cancel nomenclature")
    components_to_archive()
