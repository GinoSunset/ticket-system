"""
If task from itsm save id from links
"""

import os
import sys
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ticsys.settings")
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
django.setup()

from ticket.models import Ticket


def save_itsm_task_id_and_type_from_links():
    for ticket in Ticket.objects.filter(link_to_source__isnull=False):
        # links create by return f"{settings.ITSM_BASE_URL}/record/{type_task}/{task['sys_id']}"
        ticket.itsm_task_id = ticket.link_to_source.split("/")[-1]
        ticket.itsm_type_task = ticket.link_to_source.split("/")[-2]
        print(
            f"save {ticket.itsm_task_id} {ticket.itsm_type_task} from {ticket.link_to_source}"
        )
        ticket.save()


if __name__ == "__main__":
    save_itsm_task_id_and_type_from_links()
