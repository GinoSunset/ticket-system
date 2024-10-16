from base64 import b64encode
from collections import namedtuple
from django.conf import settings
from requests.models import Response

import logging
import requests

from additionally.models import Dictionary
from ticket.models import Ticket
from users.models import Customer, User


CustomerPersonInfo = namedtuple('Person', ['position','fullname', 'phone'])
ShopInfo = namedtuple("Shop", ["shop_id", "address", "city"])

OPERATOR_OR = "^"
STATE_DONE = 10
def get_url():
    return settings.ITSM_BASE_URL + settings.ITSM_TASK_URL


def get_url_with_assign_filter(url: str) -> str:
    return f"{url}?sysparm_query=assigned_user={settings.ITSM_USER_ID}{OPERATOR_OR}state!={STATE_DONE}"


def get_headers():
    basic = f"{settings.ITSM_USER}:{settings.ITSM_PASSWORD}"

    return {"Authorization": f"Basic {b64encode(basic.encode('utf-8')).decode()}"}


def get_with_auth_header(url, headers=None, change_to_https=False):
    headers_ = headers or {}
    headers_.update(get_headers())
    if change_to_https:
        url = url.replace("http://", "https://")
    res = requests.get(url, headers=headers_, allow_redirects=True)
    if res.status_code != 200:
        res.raise_for_status()
    return res

def get_tasks_from_itsm() -> list[dict]:
    url = get_url()
    url = get_url_with_assign_filter(url)

    response = get_with_auth_header(url)
    return process_response(response)


def process_response(response: Response) -> list[dict]:
    data = response.json()
    if data["status"] == "OK":
        return data["data"]
    raise ValueError(f"data from {response} return {data}")

def get_customer():
    customer = Customer.objects.get(username="ДетскийМир")
    return customer
   
def get_info_about_personal_customer(opened_by) ->CustomerPersonInfo:
    link_info = opened_by["link"]
    res_link_info = get_with_auth_header(url=link_info, change_to_https=True).json()
    personal_infos = res_link_info.get("data")
    if personal_infos is None:
        logging.error(f"Can not get info about user {link_info}")
        return CustomerPersonInfo(None, None, None)
    personal_info = personal_infos[0]
    fullname = personal_info.get("display_name")
    position = personal_info.get("c_ldap_position")
    phone = personal_info.get("mobile_phone")
    return CustomerPersonInfo(position,fullname,phone)

def get_info_about_shop(org_unit: dict) -> ShopInfo:
    link_info = org_unit["link"]
    res_store_info = get_with_auth_header(url=link_info, change_to_https=True).json()
    shop_infos = res_store_info.get("data")
    if shop_infos is None:
        logging.error(f"Can not get info about shop {link_info}")
        return ShopInfo(None, None, None)
    shop_info = shop_infos[0]

    return ShopInfo(
        shop_id=shop_info.get("name"),
        address=shop_info.get("address"),
        city=shop_info.get("city"),
    )


def add_shop_info(task: dict, ticket):
    info_shop = get_info_about_shop(task["org_unit"])
    ticket.shop_id = info_shop.shop_id
    ticket.address = info_shop.address
    ticket.city=info_shop.city

def add_customer(task, ticket):
    info_customer =get_info_about_personal_customer(task["opened_by"])
    ticket.position = info_customer.position
    ticket.phone = info_customer.phone
    ticket.full_name = info_customer.fullname

def create_task_from_itsm():
    tasks = get_tasks_from_itsm()
    for task in tasks:
        create_itsm_task(task)

def create_itsm_task(task:dict) -> bool:
    sap_id = task.get("number", "Undefined")
    if Ticket.objects.filter(sap_id=sap_id).exists():
        return False
    ticket = Ticket()
    ticket.sap_id = sap_id
    ticket.description = task.get("description", "Не удалось скачать описание")
    ticket.customer=get_customer()
    add_customer(task, ticket)
    add_shop_info(task, ticket)
    ticket.creator = User.objects.get(username=settings.TICKET_CREATOR_USERNAME)
    ticket.status = Dictionary.get_status_ticket("new")
    ticket.type_ticket = Dictionary.get_type_ticket(Ticket.default_type_code)
    ticket.link_to_source=f"{get_url}/{task['sys_id']}"
    ticket.source_ticket = Ticket.SourceTicket.ITSM
    ticket.save()
    logging.info(f"Add new task {ticket} from itsm")
    return True