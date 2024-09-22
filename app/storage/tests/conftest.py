import pytest
import requests

from celery import current_app
from django.conf import settings
from storage.tasks import run_sent_to_parse_invoice

@pytest.fixture
def invoice_pfd_file():
    with open(settings.BASE_DIR / "storage/tests/test-invoice.pdf", "rb") as f:
        data = f.read()
    return data


@pytest.fixture
def monkeypatch_delay_sent_to_parse_invoice(monkeypatch):
    def mock_delay(*args, **kwargs):
        return run_sent_to_parse_invoice(args[1][0], **kwargs)

    monkeypatch.setattr(current_app, "send_task", mock_delay)


@pytest.fixture
def mock_post_to_invoice_api(monkeypatch):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    def mock_post_request(url, *args, **kwargs):
        return_data = {"Chip": 1, "LCD": 2}
        return MockResponse({"success": True, "data": return_data}, 200)

    # Use monkeypatch to replace requests.post with the mock
    monkeypatch.setattr(requests, "post", mock_post_request)