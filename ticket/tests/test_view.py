import pytest
from pytest_django.asserts import assertQuerysetEqual
from django.urls import reverse
from ticket.models import Ticket
from users.models import User


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
def test_customer_see_only_self_ticket():
    assert False


@pytest.mark.django_db
def test_contractor_see():
    assert False


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
