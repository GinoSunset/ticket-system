from ticket.signals import post_save
from ticket.models import Ticket
from ticket.handlers_itsm import create_task_from_itsm

import pytest
import factory


@factory.django.mute_signals(post_save)
@pytest.mark.django_db
def test_create_task_from_itsm(mock_itsm_get_tasks, dm_customer):
    create_task_from_itsm()
    count_task_in_json = 14
    # save_task_from_itsm(tasks)
    assert Ticket.objects.count() == count_task_in_json
