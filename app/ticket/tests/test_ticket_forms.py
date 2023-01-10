import pytest

from django.urls import reverse
from ticket.forms import TicketsForm


@pytest.mark.django_db
def test_customer_form_not_field_customer_status_contractor(customer_factory, client):
    """Исполнитель, Статус, Заказчик, Плановая дата закрытия"""

    removed_field_for_customer = ["customer", "contractor", "planned_execution_date"]

    user = customer_factory()
    client.force_login(user=user)
    res = client.get(reverse("tickets-new"))
    fields = set(res.context_data["form"].fields.keys())
    expected_field = set(TicketsForm.Meta.fields)

    for i in removed_field_for_customer:
        assert not i in fields
        expected_field.remove(i)

    assert res.context_data["form"]["status"].is_hidden
    assert (
        fields == expected_field
    ), f"more than {removed_field_for_customer} removed from the form "
