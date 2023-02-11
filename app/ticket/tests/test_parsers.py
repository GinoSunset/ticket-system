import pytest

from ticket.parsers import DMParser


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
        ],
    )
    def test_city_extractor(self, address, expected):
        city = DMParser().get_city_from_address(address)
        assert city == expected

    def test_parser_dm2(self, text_dm_2):
        message_info = DMParser().parse(text_dm_2)
        assert message_info

    def test_parser_dm2_not_sign_img(self, text_dm_2):
        message_info = DMParser().parse(text_dm_2)
        assert "[cid:image004.png@01D92A6D.90491210]" not in message_info["description"]
