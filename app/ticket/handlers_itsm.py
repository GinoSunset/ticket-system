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
STATE_CANCEL = 10
STATE_DONE = 7

TYPE_TASK = {
    "156950677111866258": "itsm_incident",
    "156950616617772294": "itsm_request",
}


def get_url():
    return f"{settings.ITSM_BASE_URL}{settings.ITSM_TASK_URL}"


def get_url_with_assign_filter(url: str) -> str:
    return f"{url}?sysparm_query=assigned_user={settings.ITSM_USER_ID}{OPERATOR_OR}state!={STATE_DONE}{OPERATOR_OR}state!={STATE_CANCEL}"


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
   
def get_info_about_personal_customer(employee) -> dict:
    link_info = employee["link"]
    res_link_info = get_with_auth_header(url=link_info, change_to_https=True).json()
    personal_infos = res_link_info.get("data")
    return personal_infos


def get_personal_info(opened_by):
    link_info = opened_by["link"]
    res_link_info = get_with_auth_header(url=link_info, change_to_https=True).json()
    personal_infos = res_link_info.get("data")
    return personal_infos


def get_info_about_shop(org_unit: dict) -> ShopInfo:
    link_info = org_unit["link"]
    res_store_info = get_with_auth_header(url=link_info, change_to_https=True).json()
    shop_infos = res_store_info.get("data")
    if shop_infos is None:
        logging.error(f"Not return info about shop {link_info}")
        return ShopInfo(None, None, None)
    shop_info = shop_infos[0]

    return ShopInfo(
        shop_id=shop_info.get("name"),
        address=shop_info.get("address"),
        city=shop_info.get("city"),
    )

def add_shop_info(org_unit: dict, ticket):
    if org_unit is None:
        logging.error(f"Can not get info about shop {org_unit}")
        return
    info_shop = get_info_about_shop(org_unit)
    ticket.shop_id = info_shop.shop_id
    ticket.address = info_shop.address
    ticket.city=info_shop.city

def get_shop_info_from_user(task: dict):
    get_personal_info(task["opened_by"])


def add_customer_and_shop_info(task, ticket):
    info_customer = get_info_about_personal_customer(task["c_employee"])
    if info_customer is None:
        logging.error(f"Can not get info about user {task['c_employee']}")
        return
    personal_info = info_customer[0]

    ticket.position = personal_info.get("c_ldap_position")
    ticket.phone = personal_info.get("mobile_phone")
    ticket.full_name = personal_info.get("display_name")

    add_shop_info(personal_info.get("unit"), ticket)

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
    add_customer_and_shop_info(task, ticket)
    ticket.creator = User.objects.get(username=settings.TICKET_CREATOR_USERNAME)
    ticket.status = Dictionary.get_status_ticket("new")
    ticket.type_ticket = Dictionary.get_type_ticket(Ticket.default_type_code)
    ticket.link_to_source = create_link_to_itsm_task(task)
    ticket.source_ticket = Ticket.SourceTicket.ITSM
    ticket.save()
    logging.info(f"Add new task {ticket} from itsm")
    return True

def create_link_to_itsm_task(task):
    table_task = task.get("sys_db_table_id")
    if table_task is not None:
        type_task = TYPE_TASK.get(table_task)
        if type_task is not None:
            return f"{settings.ITSM_BASE_URL}/record/{type_task}/{task['sys_id']}"
    return f"{get_url()}/{task['sys_id']}"


def get_tickets_for_update():
    tickets = Ticket.objects.filter(source_ticket=Ticket.SourceTicket.ITSM)
    return tickets

def updates_itsm_tickets():
    tickets_for_update = get_tickets_for_update()