import pytest

from ticket.parsers import DMParser, DMV2Parser


class TestDMParser:
    def test_parser_DM(
        self, email_ticket, marked_up_text_DM_ticket, shop_id, shop_address, sap_number
    ):
        descriptor, info, added_descriptor, sign = marked_up_text_DM_ticket

        message_info = DMParser().parse(email_ticket.text)

        assert (
            message_info["description"].splitlines()
            == (descriptor + added_descriptor).strip().splitlines()
        )
        assert message_info["address"] == shop_address
        assert message_info["sap_id"] == sap_number

    def test_metadata_info(self, marked_up_text_DM_ticket):
        _, info, _, _ = marked_up_text_DM_ticket
        meta_expected = {
            "shop_id": "VM Рыбинск Космос 3111",
            "address": "Центр Рыбинск, ул. Кирилла Николаева, д.11 (Ярославская обл.)",
            "position": "Директор магазина",
            "full_name": "Корпатов Иван Иванович",
            "phone": "8-888-999-99-99",
            "sap_id": "800111258011",
            "city": "Рыбинск",
        }

        meta_data = DMParser().get_metadata(info)
        assert meta_data == meta_expected

    @pytest.mark.parametrize(
        "address, expected",
        [
            ("Поволжье Елабуга, Окружное шоссе, д.37А (Татарстан)", "Елабуга"),
            (
                "Центр Рыбинск, ул. Кирилла Николаева, д.11 (Ярославская обл.)",
                "Рыбинск",
            ),
            (
                "Юг г. Ростов-на-Дону, проспект М. Нагибина, д. 32/2",
                "Ростов-на-Дону",
            ),
            ("МО, Серпухов, б-р 65 лет Победы, д.4", "Серпухов"),
            ("Юг Сунжа ул. Суворова д. 2/2Б", "Сунжа"),
            ("Москва, ул. Святоозёрская, д.5", "Москва"),
            ("МО, п. Малаховка, Михневское ш.,3", "Малаховка"),
            ("МО го Солнечногорск, д.Голубое пр-д Тверецкий стр. 18А", "Голубое"),
            ("Щелково, мкр. Радиоцентра, 5 (Московская обл.)", "Щелково"),
            ("Центр Нижний Новгород проспект Гагарина 35 к.1", "Нижний Новгород"),
        ],
    )
    def test_city_extractor(self, address, expected):
        city = DMParser().get_city_from_address(address)
        assert city == expected

    def test_parser_dm2(self, text_dm_2):
        message_info = DMParser().parse(text_dm_2)
        assert message_info

    def test_parser_dm3(self, text_dm_3, description_dm_3):
        message_info = DMParser().parse(text_dm_3)
        assert message_info

    def test_parser_dm_without_colon(self, text_dm_without_colon):
        message_info = DMParser().parse(text_dm_without_colon)
        assert message_info["sap_id"]
        assert message_info["address"]

    def test_parser_dm2_not_sign_img(self, text_dm_2):
        message_info = DMParser().parse(text_dm_2)
        assert "[cid:image004.png@01D92A6D.90491210]" not in message_info["description"]

    def test_get_info_from_text(self, text_dm_2):
        info = DMParser().get_info_from_message(text_dm_2)
        assert info
        assert len(info.splitlines()) == 7


class TestDMV2Parser:
    def test_get_info_from_text_dm_ver_2(self, text_dm_ver_2):
        info = DMV2Parser().parse(text_dm_ver_2)
        assert info
        assert info["sap_id"] == "8001123123"
        assert info["address"]
        assert info["description"]

    def test_get_description_from_message(self, text_dm_ver_2):
        description = DMV2Parser().get_description_from_message(text_dm_ver_2, "")
        assert (
            description
            == "Пищат кассы\r\nПосле скачка напряжения,  пищат с разницей в 1 - 2 минуты.\nФото входной зоны и фото с замером прилагаю"
        )

    @pytest.mark.django_db
    def test_email_with_two_new_line(self, text_dm_with_dup_new_line, customer_factory):
        description = DMV2Parser().get_description_from_message(
            text_dm_with_dup_new_line, ""
        )
        assert (
            description
            == "ОА ТРИКОТАЖ 2-й этаж.\r\nДоброе утро.\r\n\r\nКассы работают частично.\r\n\r\nНе все реагируют на защиту"
        )


    def test_get_email_to_reply_from_text(self, text_dm_ver_2):
        email = DMV2Parser().get_email_from_text_ticket_for_reply(text_dm_ver_2)
        assert email == "favicon@email.com"