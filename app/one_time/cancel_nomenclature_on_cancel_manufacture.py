"""
script to cancel nomenclature for canceled manufacture 
"""

from imap_tools import MailBox
import os
import sys
import django
import logging


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ticsys.settings")
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
django.setup()


from manufactures.models import Manufacture, Nomenclature
from additionally.models import Dictionary, DictionaryType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def canceled_nomenclatures():
    manufactures = get_canceled_manufacture()
    for manufacture in manufactures:
        for nomenclature in manufacture.nomenclatures.all():
            if nomenclature.status == Nomenclature.Status.CANCELED:
                continue
            nomenclature.status = Nomenclature.Status.CANCELED
            nomenclature.save()


def get_canceled_manufacture():
    status_cancel = Dictionary.objects.get(code="canceled")
    manufactures = Manufacture.objects.filter(status=status_cancel)
    return manufactures


if __name__ == "__main__":
    logging.info("Starting script for cancel nomenclature")
    canceled_nomenclatures()
