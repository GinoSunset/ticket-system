import requests
from django.conf import settings


class ParserInvoice:
    api = settings.URL_INVOICE_API

    @staticmethod
    def send_to_parser(file_data):
        parse_pdf_path = "/parse-pdf/"
        response = requests.post(
            f"{ParserInvoice.api}{parse_pdf_path}", files={"file": file_data}
        )
        return response.json()
