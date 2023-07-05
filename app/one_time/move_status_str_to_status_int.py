import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ticsys.settings")
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
django.setup()

from manufactures.models import Nomenclature


def move_status_str_to_status_int():
    nomenclatures = Nomenclature.objects.all()
    for nomenclature in nomenclatures:
        if nomenclature.status == "NW":
            nomenclature.status_int = 1
        elif nomenclature.status == "IP":
            nomenclature.status_int = 2
        elif nomenclature.status == "RD":
            nomenclature.status_int = 3
        nomenclature.save()


if __name__ == "__main__":
    move_status_str_to_status_int()
