import logging
from ticsys import celery_app
from storage.models import Invoice, Alias, InvoiceAliasRelation
from storage.microservices import ParserInvoice


@celery_app.task
def sent_to_parse_invoice(pk):
    return run_sent_to_parse_invoice(pk)


def run_sent_to_parse_invoice(pk):
    invoice: Invoice = Invoice.objects.get(pk=pk)
    invoice.status = Invoice.Status.WORK
    invoice.save()
    file = invoice.file_invoice.file.name
    with open(file, "rb") as f:
        file_data = f.read()
    try:
        result = ParserInvoice.send_to_parser(file_data)
    except Exception as e:
        logging.error(f"task parse invoice error: {e}")
        invoice.status = Invoice.Status.ERROR
        invoice.save()
        return

    if aliases := result.get("results"):
        for alias_from_invoice, count in aliases.items():
            alias, _ = Alias.objects.get_or_create(name=alias_from_invoice)
            InvoiceAliasRelation.objects.create(
                alias=alias, invoice=invoice, quantity=count
            )
    # TODO: results['errors']
    invoice.status = Invoice.Status.DONE
    invoice.save()
    return result
