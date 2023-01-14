import pytest
from imap_tools.message import MailMessage
from django.conf import settings


@pytest.fixture
def email_ticket():
    with open(settings.BASE_DIR / "ticket/tests/email.eml", "rb") as f:
        data = f.read()
    mail = MailMessage.from_bytes(data)
    return mail
