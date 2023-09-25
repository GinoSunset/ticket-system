import re

from collections import defaultdict
from natasha import AddrExtractor, MorphVocab
import logging

RE_IDENTIFIER_CITY = re.compile(r"(?<!\w)г\.|(?<!\w)город\s")


class BaseParser:
    def parse(self, text) -> dict:
        return {"description": text}

    @classmethod
    def get_parser(cls, parser_name: str, is_html: bool) -> "BaseParser":
        parsers = {
            "base": BaseParser(),
            "DM": DMParser(),
            "DMV2": DMV2Parser(),
            "DMV2_html": DMV2ParseHTML(),
        }
        if is_html:
            return parsers.get(f"{parser_name}_html", BaseParser())
        return parsers.get(parser_name, BaseParser())


class DMParser(BaseParser):
    def __init__(self):
        self.sap_str = "SAP"
        self.sap_delimiter = ":"
        self.sign_text = "С уважением"

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
        index_sign = text.find(self.sign_text)
        if index_sign == -1:
            additional_text = text[index:]
        else:
            additional_text = text[index:index_sign]
        text = self.remove_cid_lines(additional_text)
        return text

    def get_info_from_message(self, text):
        text_before_sign = text.split(self.sign_text)[0]

        lines = text_before_sign.splitlines()
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
                key, value = line.split(":", maxsplit=1)
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
                if city := self.get_city_from_address(result["address"]):
                    result["city"] = city
            except Exception as e:
                logging.error(f"Error in get city from address: {e}")
        return result

    def return_str_in_list_with_str(self, list_str: list, str: str) -> str:
        return list(filter(lambda x: str in x, list_str))[0]

    def get_city_from_address(self, address):
        region, address_2 = address.split(" ", maxsplit=1)
        if not RE_IDENTIFIER_CITY.search(address):
            if "москва" in region.lower():
                return "Москва"
            address = f"{region} г. {address_2}"
        morph_vocab = MorphVocab()
        city = self.morph_city(address, morph_vocab)
        if not city:
            region, address_2 = address.split(" ", maxsplit=1)
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


class DMV2Parser(DMParser):
    def __init__(self):
        self.email_regexp = r"(?:mailto:)([\w'._+-]+@[\w'._+-]+)"
        self.start_email_text = "Вы можете связаться с заказчиком"
        self.sap_str = "сервисный запрос"
        self.sap_str_incident = "назначен инцидент"
        self.sap_delimiter = "под номером "
        self.meta_data_map = {
            "Магазин/Департамент": "shop_id",
            "Регион": "address",
            "Должность": "position",
            "Ф.И.О.": "full_name",
            "Телефон": "phone",
            "SAP": "sap_id",
            "Имя/IP адрес ПК": "metadata",
            "Дата регистрации": "metadata",
        }
        self.sign_text = (
            "Это сообщение создано автоматически, пожалуйста, не отвечайте на него."
        )

    def parse(self, text) -> dict:
        descriptor, info, additional_text = self.split_text_to_parts(text)

        meta_data = self.get_metadata(info)
        email_current_customer_email = self.get_email_from_text_ticket_for_reply(additional_text)
        if not "sap_id" in meta_data:
            meta_data["sap_id"] = self.get_sap_id_from_text(text)

        result = {
            "description": (descriptor + additional_text).strip(),
            "sap_id": meta_data["sap_id"],
        }
        result.update(meta_data)
        if email_current_customer_email:
            result["email_current_customer_email"] = email_current_customer_email
        return result

    def split_text_to_parts(self, text):
        info = self.get_info_from_message(text)
        description = self.get_description_from_message(text, info)
        additional_text = self.get_additional_text_from_message(text, info, description)
        return description, info, additional_text

    def get_description_from_message(self, text, info):
        theme = self.get_theme_from_message(text)
        description = self.get_description_lines(text)
        if theme.lower() in description.lower():
            return description
        return f"{theme}\r\n{description}"

    def get_theme_from_message(self, text):
        theme_line = [line for line in text.splitlines() if "Тема:" in line][0]
        theme = theme_line.split("Тема:")[1].strip()
        return theme

    def get_description_lines(self, text):
        index_start = text.index("Описание:")
        end_index = self.get_end_index(text, index_start)

        description_lines = text[index_start:end_index]
        return description_lines[len("Описание:") :].strip()

    def get_sap_id_from_text(self, text):
        if self.sap_str not in text:
            if not self.sap_str_incident in text:
                raise ValueError("Not found SAP in text")
            self.sap_str = self.sap_str_incident
        return super().get_sap_id_from_text(text)
    
    def get_end_index(self, text, index_start):
        index_start += len("Описание:")

        end_index = text[index_start:].find(":")
        if end_index != -1:
            last_line_index = text[index_start : index_start + end_index].rfind("\n")
            if last_line_index != -1:
                return last_line_index + index_start

        dup_empty_line = "\r\n\r\n"

        end_index = text[index_start:].find(dup_empty_line)
        if end_index == -1:
            end_index = text[index_start:].find("\n\n")
        if end_index == -1:
            end_index = text[index_start:].index("\n")
        return end_index + index_start

    def get_email_from_text_ticket_for_reply(self, text):
        "Получить email из текста тикета для ответа на него"
        for i in text.splitlines():
            if self.start_email_text in i:
                match = re.search(self.email_regexp, i)
                if match:
                    logging.info(f"Found current email for reply into text ticket: {match.group(1)}")
                    return match.group(1)
                logging.info(f"Not found current email for reply into text ticket")
        

class DMV2ParseHTML(DMV2Parser):
    def __init__(self):
        super().__init__()
        self.html: str = ""

    def parse(self, html):
        self.html = html
        text = self.html_to_text()
        return super().parse(text)

    def html_to_text(self) -> str:
        text = self.convert_br()
        text = self.remove_header_html(text)
        return text

    def remove_header_html(self, text: str) -> str:
        return text.replace("<html>", "").replace("</html>", "")

    def convert_br(self) -> str:
        return self.html.replace("<br>", "\r\n")
