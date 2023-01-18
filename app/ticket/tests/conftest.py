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


@pytest.fixture
def text_reply():
    return """Вот так\r\n\r\n> 17 янв. 2023 г., в 00:44, Yandex <akimov-pnz@yandex.ru> написал(а):\r\n> \r\n> Прошу принять в работу заявку:\r\n> \r\n> Срабатывают противокражные рамки без причины.\r\n> \r\n> Платы стоят ИНОМАТИК\r\n>  \r\n> Телефон:89393639660\r\n> Ф.И.О.: Зайнулина Линара Рифатовна\r\n> Должность: Заместитель директора магазина\r\n> Магазин/Департамент: ДМ Елабуга Эссен 2883\r\n> Регион: Поволжье Елабуга, Окружное шоссе, д.37А (Татарстан)\r\n> \r\n> SAP: 8001118269\r\n> \r\n> Предоставить фото входной группы, расстояния между антенн с рулеткой где видно расстояния.\r\n> \r\n> Без данного фото работы приняты не будут\r\n> \r\n>  \r\n> \r\n>  \r\n> \r\n> <cid:image001.png@01D4F46F.E0E617F0>\r\n> С уважением, \r\n> \r\n> Потапов Виктор Александрович\r\n> \r\n> Менеджер по системам безопасности и видеонаблюдению\r\n> \r\n> Департамента по ИТ ПАО "Детский мир".\r\n> \r\n>  \r\n> +7 916 693-79-29\r\n> \r\n> +7 495 781-08-08 доб. 25-53\r\n> \r\n> VAPotapov@detmir.ru <mailto:VAPotapov@detmir.ru>\r\n> Детский мир\r\n> \r\n> 127238, Москва, 3-й Нижнелихоборский пр., д. 3, стр. 6 \r\n> \r\n> www.detmir.ru <http://www.detmir.ru/>\r\n> \r\n> <image004.png>\r\n> \r\n\r\n"""
