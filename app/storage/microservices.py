import requests
from django.conf import settings


class ParserInvoice:
    api = settings.URL_INVOICE_API

    @staticmethod
    def send_to_parser(file_data):
        response = requests.post(ParserInvoice.api, files={"file": file_data})
        return response.json()
