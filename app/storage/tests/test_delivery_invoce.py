import pytest
from django.test import override_settings
import tempfile

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from storage.models import Delivery, Invoice
from storage.views.delivery import UpdateInvoice

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
@pytest.mark.django_db
def test_upload_file(
    operator_client,
    invoice_pfd_file,
    monkeypatch_delay_sent_to_parse_invoice,
    mock_post_to_invoice_api,
):
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
    assert delivery.invoice.status == Invoice.Status.DONE

@pytest.mark.django_db
def test_success_form_invoice_go_to_set_delivery(
    operator_client,
    invoice_pfd_file,
    monkeypatch_delay_sent_to_parse_invoice,
    mock_post_to_invoice_api,
):
    uploaded_file = SimpleUploadedFile(
        "test-invoice.pdf", invoice_pfd_file, content_type="application/pdf"
    )
    data = {"date_delivery": "2022-01-01", "file_invoice": uploaded_file}
    url = reverse("create-delivery-invoice")

    response = operator_client.post(url, data, format="multipart")

    assert response.status_code == 302
    assert response.url == reverse("update-invoice")

@pytest.mark.django_db
def test_form_update_invoice_has_only_need_alias(invoice_factory, invoice_alias_relation_factory):
    i1 = invoice_factory()
    i2 = invoice_factory()
    ir_1 = invoice_alias_relation_factory.create_batch(5, invoice=i1)
    ir_2 = invoice_alias_relation_factory.create_batch(5, invoice=i2)
    view = UpdateInvoice()
    view.object = i1.delivery

    fs = view.get_formset()
    assert len(fs.forms) == 5


@pytest.mark.django_db
def test_get_formset_initialization(invoice_factory, invoice_alias_relation_factory):
    i1 = invoice_factory()
    i2 = invoice_factory()
    ir_1 = invoice_alias_relation_factory(invoice=i1, quantity=16)
    ir_2 = invoice_alias_relation_factory(invoice=i1, quantity=120)
    ir_3 = invoice_alias_relation_factory(invoice=i1, quantity=7)

    invoice_alias_relation_factory.create_batch(5, invoice=i2)
    view = UpdateInvoice()
    view.object = i1.delivery

    fs = view.get_formset()
    # Проверяем, что formset был инициализирован с правильными данными
    assert fs.forms[0].initial["quantity"] == 16
    assert fs.forms[1].initial["quantity"] == 120
    assert fs.forms[2].initial["quantity"] == 7
    assert fs.forms[0].initial["id"] == ir_1.alias.id
    assert fs.forms[1].initial["id"] == ir_2.alias.id
    assert fs.forms[2].initial["id"] == ir_3.alias.id

    # Проверяем, что правильный компонент был выбран
    assert fs.forms[0].initial["name"] == ir_1.alias.name
    assert fs.forms[0].initial["name"] == ir_2.alias.name
    assert fs.forms[2].initial["name"] == ir_3.alias.name


@pytest.mark.django_db
def test_for_invoice_alias_invalid_if_has_empty_field():
    pass

@pytest.mark.django_db
def test_error_invoice_save_error():
    assert False

def test_remove_aliases_set_comment_to_rel_alias_invoice():
    assert False