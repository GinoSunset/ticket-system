import pytest
from django.test import override_settings
import tempfile

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from storage.models import Delivery, Invoice


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
@pytest.mark.django_db
def test_upload_file(operator_client, invoice_pfd_file):
    uploaded_file = SimpleUploadedFile(
        "test-invoice.pdf", invoice_pfd_file, content_type="application/pdf"
    )
    data = {"date_delivery": "2022-01-01", "file_invoice": uploaded_file}
    url = reverse("create-delivery-invoice")

    response = operator_client.post(url, data, format="multipart")

    assert response.status_code == 302
    assert Delivery.objects.count() == 1
    delivery = Delivery.objects.first()
    assert delivery
    assert delivery.status == Delivery.Status.DRAFT
    assert "test-invoice.pdf" in delivery.invoice.file_invoice.name
    assert delivery.invoice.status == Invoice.Status.WORK
