import pytest
import factory

from django.urls import reverse
from django.db.models import signals
from ticket.forms import TicketsForm
from additionally.models import Dictionary, DictionaryType

from users.models import CustomerProfile
from notifications.models import Notification


@pytest.mark.django_db
def test_customer_form_not_field_customer_status_contractor(customer_factory, client):
    """Исполнитель, Статус, Заказчик, Плановая дата закрытия, Ответственный не должны быть в форме для заказчика"""

    removed_field_for_customer = [
        "customer",
        "contractor",
        "planned_execution_date",
        "responsible",
    ]

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


@pytest.mark.django_db
@factory.django.mute_signals(signals.pre_save, signals.post_save)
def test_create_notify_when_set_contractor(
    operator_factory, contractor_factory, customer_factory, ticket_factory, client
):
    """Проверка создания уведомления при назначении исполнителя"""
    user = operator_factory()
    customer = customer_factory()
    cp = CustomerProfile.objects.create(user=customer)
    user.customers.add(cp)
    contractor = contractor_factory()
    ticket = ticket_factory(customer=customer)
    client.force_login(user=user)
    res = client.post(
        reverse("ticket-update", kwargs={"pk": ticket.pk}),
        data={
            "contractor": contractor.pk,
            "description": ticket.description,
            "customer": customer.pk,
        },
    )
    assert Notification.objects.filter(user=contractor).count() == 1


@pytest.mark.django_db
@factory.django.mute_signals(signals.pre_save, signals.post_save)
def test_save_ticket_type_before_update_ticket(
    operator_factory, contractor_factory, customer_factory, ticket_factory, client
):
    """Проверка создания уведомления при назначении исполнителя"""
    user = operator_factory()
    customer = customer_factory()
    cp = CustomerProfile.objects.create(user=customer)
    user.customers.add(cp)
    contractor = contractor_factory()
    type_ticket = Dictionary.objects.create(
        code="test_save_ticket_type_before_update_ticket",
        type_dict=DictionaryType.objects.get(code="status_ticket"),
    )
    ticket = ticket_factory(
        customer=customer,
        type_ticket=type_ticket,
    )

    client.force_login(user=user)
    res = client.get(
        reverse("ticket-update", kwargs={"pk": ticket.pk}),
    )
    assert res.context_data["form"].fields["type_ticket"].initial == type_ticket
