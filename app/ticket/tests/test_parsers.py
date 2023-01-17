import pytest

from ticket.parsers import DMParser


class TestDMParser:
    def test_parser_DM(
        self, email_ticket, marked_up_text_DM_ticket, shop_id, shop_address, sap_number
    ):
        descriptor, info, added_descriptor, sign = marked_up_text_DM_ticket

        message_info = DMParser().parse(email_ticket.text)

        assert message_info["description"] == (descriptor + added_descriptor).strip()
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
        ],
    )
    def test_city_extractor(self, address, expected):
        city = DMParser().get_city_from_address(address)
        assert city == expected
