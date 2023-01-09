import pytest
from django.urls import reverse
from ticket.models import Ticket
from users.models import User, Customer, Contractor
from additionally.models import Dictionary


@pytest.mark.django_db
def test_user_see_ticket_their_customer(
    ticket_factory, user_factory, client, customer_factory
):
    operator: User = user_factory(role=User.Role.OPERATOR)
    operator = operator.get_role_user()
    their_customer = customer_factory()
    other_customer = customer_factory()
    operator.customers.add(their_customer.profile)
    ticket: Ticket = ticket_factory(customer=their_customer)
    ticket_another = ticket_factory(customer=other_customer)

    client.force_login(user=operator)
    response = client.get(reverse("tickets-list"))

    assert len(response.context_data["ticket_list"]) == 1
    assert response.context_data["ticket_list"][0] == ticket


@pytest.mark.django_db
def test_customer_see_only_self_ticket(
    ticket_factory, user_factory, client, customer_factory
):
    operator = user_factory(role=User.Role.OPERATOR)
    customer: Customer = customer_factory()
    other_customer = customer_factory()
    ticket_another: Ticket = ticket_factory(customer=other_customer, creator=operator)
    ticket: Ticket = ticket_factory(customer=customer, creator=operator)

    client.force_login(user=customer)
    response = client.get(reverse("tickets-list"))

    assert len(response.context_data["ticket_list"]) == 1
    assert response.context_data["ticket_list"][0] == ticket


@pytest.mark.django_db
def test_contractor_see(ticket_factory, user_factory, client, customer_factory):
    operator = user_factory(role=User.Role.OPERATOR)
    customer: Customer = customer_factory()
    contractor: Contractor = user_factory(role=User.Role.CONTRACTOR)
    other_customer = customer_factory()
    ticket_another: Ticket = ticket_factory(customer=other_customer, creator=operator)
    ticket: Ticket = ticket_factory(
        customer=customer, creator=operator, contractor=contractor
    )

    client.force_login(user=contractor)
    response = client.get(reverse("tickets-list"))

    assert len(response.context_data["ticket_list"]) == 1
    assert response.context_data["ticket_list"][0] == ticket


@pytest.mark.django_db
def test_admin_see_all_ticket(ticket_factory, user_factory, client):
    user1 = user_factory()
    admin_user = user_factory(is_staff=True)
    user_another = user_factory()
    ticket: Ticket = ticket_factory(creator=user1)
    ticket_another = ticket_factory(creator=user_another)
    client.force_login(user=admin_user)
    response = client.get(reverse("tickets-list"))
    assert list(response.context_data["ticket_list"]), list(Ticket.objects.all())


@pytest.mark.django_db
def test_access_page_generate_task_customer(customer_factory, client):
    customer = customer_factory()
    client.force_login(user=customer)
    res = client.get(reverse("tickets-new"))
    assert res.status_code == 200


@pytest.mark.django_db
def test_access_page_generate_task_contractor(user_factory, client):
    contractor = user_factory(role=User.Role.CONTRACTOR)
    client.force_login(user=contractor)
    res = client.get(reverse("tickets-new"))
    assert res.status_code == 200


@pytest.mark.django_db
def test_access_page_update_task_contractor(ticket_factory, user_factory, client):
    contractor = user_factory(role=User.Role.CONTRACTOR)
    ticket = ticket_factory(contractor=contractor)
    client.force_login(user=contractor)
    res = client.get(reverse("ticket-update", kwargs={"pk": ticket.pk}))
    assert res.status_code == 200


@pytest.mark.django_db
def test_access_page_update_task_customer(ticket_factory, customer_factory, client):
    customer = customer_factory()
    ticket = ticket_factory(customer=customer)
    client.force_login(user=customer)
    res = client.get(reverse("ticket-update", kwargs={"pk": ticket.pk}))
    assert res.status_code == 200


@pytest.mark.django_db
def test_access_page_update_task_other(ticket_factory, user_factory, client):
    user = user_factory(role=User.Role.OTHER)
    ticket: Ticket = ticket_factory(creator=user)
    client.force_login(user=user)
    res = client.get(reverse("ticket-update", kwargs={"pk": ticket.pk}))
    assert res.status_code == 200


@pytest.mark.django_db
def test_access_page_create_task_other(user_factory, client):
    user = user_factory(role=User.Role.OTHER)
    client.force_login(user=user)
    res = client.get(reverse("tickets-new"))
    assert res.status_code == 200


@pytest.mark.django_db
def test_customer_form_not_field_customer_status_contractor(customer_factory, client):
    """Исполнитель, Статус, Заказчик"""
    user = customer_factory()
    client.force_login(user=user)
    res = client.get(reverse("tickets-new"))
    fields = set(res.context_data["form"].fields.keys())
    assert not "customer" in fields
    assert not "status" in fields
    assert not "contractor" in fields


@pytest.mark.django_db
def test_customer_save_ticket_has_all_needed_field(customer_factory, client):
    """Исполнитель, Статус, Заказчик"""
    user = customer_factory()
    client.force_login(user=user)
    data = {"description": "bla", "city": "17", "address": "1"}

    res = client.post(reverse("tickets-new"), data=data)

    assert res.status_code == 302

    ticket = Ticket.objects.first()
    assert ticket.creator == user
    assert ticket.customer == user
    assert ticket.status == Dictionary.objects.get(code="work")
    assert ticket.contractor is None
