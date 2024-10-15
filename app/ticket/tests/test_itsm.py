from ticket.signals import post_save
from ticket.models import Ticket
from ticket.handlers_itsm import (
    create_task_from_itsm,
    get_info_about_personal_customer,
    get_info_about_shop,
)

import pytest
import factory


@factory.django.mute_signals(post_save)
@pytest.mark.django_db
def test_create_task_from_itsm(mock_itsm_request, dm_customer):
    create_task_from_itsm()
    count_task_in_json = 4
    # save_task_from_itsm(tasks)
    assert Ticket.objects.count() == count_task_in_json

def test_get_info_about_personal_customer(mock_itsm_request):
    personal_info = get_info_about_personal_customer(
        {"link": "http://test.com/personal/test-id"}
    )
    assert personal_info.fullname is not None
    assert personal_info.position is not None
    assert personal_info.phone is not None


def test_get_info_about_shop(mock_itsm_request):
    shop_info = get_info_about_shop({"link": "***************/org_unit/test-id"})
    assert shop_info.city is None
    assert shop_info.shop_id is not None
    assert shop_info.address is None