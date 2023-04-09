from collections import defaultdict
from natasha import AddrExtractor, MorphVocab
import logging


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
    def __init__(self):
        self.sap_str = "SAP"
        self.sap_delimiter = ":"

        self.meta_data_map = {
            "Магазин/Департамент": "shop_id",
            "Регион": "address",
            "Должность": "position",
            "Ф.И.О.": "full_name",
            "Телефон": "phone",
            "SAP": "sap_id",
            "Имя/IP адрес ПК": "metadata",
        }

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
        self.sap_delimiter = ":" if "SAP:" in text else " "

        descriptor, info, additional_text = self.split_text_to_parts(text)

        meta_data = self.get_metadata(info)

        if not "sap_id" in meta_data:
            meta_data["sap_id"] = self.get_sap_id_from_text(text)

        result = {
            "description": (descriptor + additional_text).strip(),
            "sap_id": meta_data["sap_id"],
        }
        result.update(meta_data)
        return result

    def split_text_to_parts(self, text):
        info = self.get_info_from_message(text)
        description = self.get_description_from_message(text, info)
        additional_text = self.get_additional_text_from_message(text, info, description)
        return description, info, additional_text

    def get_description_from_message(self, text, info):
        first_info_line = info.splitlines()[0]
        index_info = text.find(first_info_line)
        if index_info == -1:
            return ""
        description = text[:index_info]
        return description

    def get_additional_text_from_message(self, text, info, description):
        last_info_line = info.splitlines()[-1]
        last_start_index = text.rfind(last_info_line)
        index = last_start_index + len(last_info_line)
        index_sign = text.find("С уважением")
        if index_sign == -1:
            additional_text = text[index:]
        else:
            additional_text = text[index:index_sign]
        text = self.remove_cid_lines(additional_text)
        return text

    def get_info_from_message(self, text):
        lines = text.splitlines()
        info = [
            line
            for line in lines
            if ":" in line and line.split(":")[0].strip() in self.meta_data_map
        ]
        return "\r\n".join(info)

    def remove_cid_lines(self, text):
        lines = text.splitlines()
        lines = [line for line in lines if "[cid:" not in line]
        return "\r\n".join(lines)

    def get_sap_id_from_text(self, text):
        index_start_sap_line, index_end_sap_line = self.get_indexes_sap(text)
        sap = text[index_start_sap_line:index_end_sap_line]
        sap = sap.split(self.sap_delimiter)[1].strip()
        return sap

    def get_indexes_sap(self, text):
        index_start_sap_line = text.find(self.sap_str)
        index_end_sap_line = text[index_start_sap_line:].find("\n")
        if index_end_sap_line == -1:
            index_end_sap_line = text[index_start_sap_line:].find("</p>")
        index_end_sap_line = index_end_sap_line + index_start_sap_line
        return index_start_sap_line, index_end_sap_line

    def get_metadata(self, info: str) -> dict:

        lines = info.splitlines()
        if len(lines) == 1:
            lines = info.split("</p>")
        lines = [line.strip() for line in lines if line.strip()]

        result = defaultdict(str)
        for line in lines:
            if not line:
                continue
            line = line.strip()
            if ":" in line:
                key, value = line.split(":")
            else:
                key, value = line.split(" ", maxsplit=1)
            if key in self.meta_data_map:
                if self.meta_data_map[key] == "metadata":
                    result[self.meta_data_map[key]] += line
                    continue
                result[self.meta_data_map[key]] = value.strip()
                continue

            result["metadata"] += line
        if result["address"]:
            try:
                result["city"] = self.get_city_from_address(result["address"])
            except Exception as e:
                logging.error(f"Error in get city from address: {e}")
        return result

    def return_str_in_list_with_str(self, list_str: list, str: str) -> str:
        return list(filter(lambda x: str in x, list_str))[0]

    def get_city_from_address(self, address):
        if "г." not in address and "город " not in address:
            region, address_2 = address.split(" ", maxsplit=1)
            if "москва" in region.lower():
                return "Москва"
            address = f"{region} г. {address_2}"
        morph_vocab = MorphVocab()
        city = self.morph_city(address, morph_vocab)
        if not city:
            address = f"г. {region}"
            city = self.morph_city(address, morph_vocab)
        return city

    def morph_city(self, address, morph_vocab):

        extractor = AddrExtractor(morph_vocab)
        matches = extractor(address)
        tokens = list(matches)
        for token in tokens:
            if token.fact.type in ("город", "посёлок", "деревня"):
                city = token.fact.value
                return city
