import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from storage.models import Delivery


@pytest.mark.django_db
def test_upload_file(operator_client, invoice_pfd_file):
    uploaded_file = SimpleUploadedFile(
        "test-invoice.pdf", invoice_pfd_file, content_type="application/pdf"
    )
    data = {"file": uploaded_file}
    url = reverse("create-delivery-invoice")

    response = operator_client.post(url, data, format="multipart")

    assert response.status_code == 302
    assert Delivery.objects.count() == 1
    delivery = Delivery.objects.first()
    assert delivery
    assert delivery.invoice.file_invoice.name == "test-invoice.pdf"
