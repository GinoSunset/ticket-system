import pytest
from django.conf import settings


@pytest.fixture
def invoice_pfd_file():
    with open(settings.BASE_DIR / "storage/tests/test-invoice.pdf", "rb") as f:
        data = f.read()
    return data
