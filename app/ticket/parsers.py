from collections import defaultdict
from natasha import AddrExtractor, MorphVocab


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

        index_start_sap_line, index_end_sap_line = self.get_indexes_sap(text)

        sap = self.get_sap(text, index_start_sap_line, index_end_sap_line)

        index_sign = text.find("С уважением")

        additional_text = text[index_end_sap_line:index_sign]

        meta_data = self.get_metadata(info)
        result = {
            "description": (descriptor + additional_text).strip(),
            "sap_id": sap,
        }
        result.update(meta_data)
        return result

    def get_sap(self, text, index_start_sap_line, index_end_sap_line):
        sap = text[index_start_sap_line:index_end_sap_line]
        sap = sap.split(":")[1].strip()
        return sap

    def get_indexes_sap(self, text):
        index_start_sap_line = text.find("SAP:")

        index_end_sap_line = text[index_start_sap_line:].find("\n")
        if index_end_sap_line == -1:
            index_end_sap_line = text[index_start_sap_line:].find("</p>")
        index_end_sap_line = index_end_sap_line + index_start_sap_line
        return index_start_sap_line, index_end_sap_line

    def get_metadata(self, info: str) -> dict:
        meta_data_map = {
            "Магазин/Департамент": "shop_id",
            "Регион": "address",
            "Должность": "position",
            "Ф.И.О.": "full_name",
            "Телефон": "phone",
            "SAP": "sap_id",
        }
        lines = info.splitlines()
        if len(lines) == 1:
            lines = info.split("</p>")

        result = defaultdict(str)
        for line in lines:
            if not line:
                continue
            if ":" in line:
                key, value = line.split(":")
            else:
                key, value = line.split(" ", maxsplit=1)
            if key in meta_data_map:
                result[meta_data_map[key]] = value.strip()
                continue

            result["other_meta_info"] += line
        if result["address"]:
            result["city"] = self.get_city_from_address(result["address"])
        return result

    def return_str_in_list_with_str(self, list_str: list, str: str) -> str:
        return list(filter(lambda x: str in x, list_str))[0]

    def get_city_from_address(self, address):
        morph_vocab = MorphVocab()
        extractor = AddrExtractor(morph_vocab)
        matches = extractor(address)
        tokens = list(matches)
        for token in tokens:
            if token.fact.type == "город":
                return token.fact.value
        city_with_district = address.split(",")[0]
        city = city_with_district.split(" ", maxsplit=1)[1]
        city = city.removeprefix("г.").strip()
        return city
