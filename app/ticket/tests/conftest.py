import pytest
from imap_tools.message import MailMessage
from django.conf import settings


@pytest.fixture
def email_ticket():
    with open(settings.BASE_DIR / "ticket/tests/email.eml", "rb") as f:
        data = f.read()
    mail = MailMessage.from_bytes(data)
    return mail


@pytest.fixture
def shop_id():
    return "VM Рыбинск Космос 3111"


@pytest.fixture
def shop_address():
    return "Центр Рыбинск, ул. Кирилла Николаева, д.11 (Ярославская обл.)"


@pytest.fixture
def sap_number():
    return "800111258011"


@pytest.fixture
def marked_up_text_DM_ticket(shop_id, shop_address, sap_number):
    descriptor = """Добрый день

Прошу принять в работу заявку:

Ложное срабатывание антикражных рамок и интервалом в 1 минуту.

"""
    info = f"""Телефон:8-888-999-99-99
Ф.И.О.: Корпатов Иван Иванович
Должность: Директор магазина
Магазин/Департамент: {shop_id}
Регион: {shop_address}

SAP: {sap_number}

"""
    added_descriptor = """

Предоставить фото входной группы, расстояния между антенн с рулеткой где 
видно расстояния.

Без данного фото работы приняты не будут




"""
    sign = """С уважением,

Потапов Виктор Александрович

Менеджер по системам безопасности и видеонаблюдению

Департамента по ИТ ПАО "Детский мир".
"""
    return descriptor, info, added_descriptor, sign
