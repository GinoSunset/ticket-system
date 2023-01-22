import pytest

from django.urls import reverse
from users.models import User


def test_not_access_for_not_logged_user(client):
    res = client.get(reverse("tickets-list"))
    assert res.status_code == 302
    assert "/accounts/login/?next" in res.url


@pytest.mark.django_db
def test_not_access_for_customer(ticket_factory, customer_factory, client):
    customer = customer_factory()
    ticket = ticket_factory(customer=customer_factory())
    client.force_login(user=customer)
    res = client.get(reverse("ticket-update", kwargs={"pk": ticket.pk}))
    assert res.status_code == 403


@pytest.mark.django_db
def test_not_access_for_contractor(ticket_factory, user_factory, client):
    user = user_factory(role=User.Role.CONTRACTOR)
    ticket = ticket_factory(customer=user_factory(role=User.Role.CUSTOMER))
    client.force_login(user=user)
    res = client.get(reverse("ticket-update", kwargs={"pk": ticket.pk}))
    assert res.status_code == 403


@pytest.mark.django_db
def test_has_access_for_contractor(ticket_factory, user_factory, client):
    user = user_factory(role=User.Role.CONTRACTOR)
    ticket = ticket_factory(contractor=user)
    client.force_login(user=user)
    res = client.get(reverse("ticket-update", kwargs={"pk": ticket.pk}))
    assert res.status_code == 200


@pytest.mark.django_db
def test_not_access_for_operator(
    operator_factory, ticket_factory, customer_factory, client
):
    operator = operator_factory()
    ticket = ticket_factory(customer=customer_factory())
    client.force_login(user=operator)
    res = client.get(reverse("ticket-update", kwargs={"pk": ticket.pk}))
    assert res.status_code == 403


@pytest.mark.django_db
def test_has_access_for_operator(
    operator_factory, ticket_factory, customer_factory, client
):
    operator = operator_factory()
    customer = customer_factory()
    operator.customers.add(customer.profile)
    ticket = ticket_factory(customer=customer)
    client.force_login(user=operator)
    res = client.get(reverse("ticket-update", kwargs={"pk": ticket.pk}))
    assert res.status_code == 200
