"""
script for re reserve component in stock
"""

import os
import sys
import django
import logging


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ticsys.settings")
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
django.setup()


from storage.reserve import re_reserver_components_in_stock_to_phantoms

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def re_reserve_components_in_stock():
    re_reserver_components_in_stock_to_phantoms()


if __name__ == "__main__":
    logging.info("Starting script for re reservation ")
    re_reserve_components_in_stock()
