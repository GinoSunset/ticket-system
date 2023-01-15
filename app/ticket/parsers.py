class BaseParser:
    def parse(self, text) -> dict:
        return {"description": text}

    @classmethod
    def get_parser(cls, parser_name: str) -> "BaseParser":
        parsers = {
            "base": BaseParser(),
            "DM": DMParser(),
        }

        return parsers.get(parser_name, BaseParser())


class DMParser(BaseParser):
    def parse(self, text) -> dict:
        """

        Добрый день
        Прошу принять в работу заявку:
        Ложное срабатывание антикражных рамок и интервалом в 1 минуту.

        Телефон:8-888-999-99-99
        Ф.И.О.: Корпатов Иван Иванович
        Должность: Директор магазина
        Магазин/Департамент: VM Рыбинск Космос 3111
        Регион: Центр Рыбинск, ул. Кирилла Николаева, д.11 (Ярославская обл.)
        SAP: 80011121111

        Предоставить фото входной группы, расстояния между антенн с рулеткой где
        видно расстояния.
        Без данного фото работы приняты не будут

        С уважением,
        Коратов Виктор Александрович
        Менеджер по системам безопасности и видеонаблюдению
        Департамента по ИТ ПАО "VIM".

        message_info["description"] == descriptor + added_descriptor
        message_info["metadata"] == shop_id
        message_info["address"] == shop_address
        message_info["sap_id"] == sap_number
        """

        descriptor = text[: text.find("Телефон:")]
        info = text[text.find("Телефон:") : text.find("SAP:")]

        index_start_sap_line = text.find("SAP:")
        index_end_sap_line = (
            text[index_start_sap_line:].find("\n") + index_start_sap_line
        )

        sap = text[index_start_sap_line:index_end_sap_line]
        sap = sap.split(":")[1].strip()

        index_sign = text.find("С уважением,")

        additional_text = text[index_end_sap_line:index_sign]

        shop_id, address = self.get_metadata(info)
        return {
            "description": (descriptor + additional_text).strip(),
            "metadata": shop_id,
            "address": address,
            "sap_id": sap,
        }

    def get_metadata(self, info: str) -> dict:
        lines = info.splitlines()

        shop_lines = self.return_str_in_list_with_str(lines, "Магазин/Департамент:")
        address_lines = self.return_str_in_list_with_str(lines, "Регион:")
        shop_id = shop_lines.split(":")[1].strip()
        address = address_lines.split(":")[1].strip()
        return shop_id, address

    def return_str_in_list_with_str(self, list_str: list, str: str) -> str:
        return list(filter(lambda x: str in x, list_str))[0]
