import pytest
import json
import factory

from django.urls import reverse
from django.db.models import signals
from share.models import Share
from ticket.models import Ticket

from users.models import CustomerProfile


@factory.django.mute_signals(signals.pre_save, signals.post_save)
@pytest.mark.django_db
def test_create_share_ticket(
    ticket_factory, client, operator_factory, customer_factory
):
    customer = customer_factory()
    customer.refresh_from_db()
    operator = operator_factory()
    CustomerProfile.objects.create(user=customer)
    customer.profile.linked_operators.add(operator)

    ticket = ticket_factory(customer=customer)
    url = reverse("create-share")
    client.force_login(operator)
    response = client.post(url, data={"ticket": ticket.id}, format="json")
    data = json.loads(response.content)
    ticket.refresh_from_db()
    assert response.status_code == 200
    assert data.get("uuid") == str(ticket.share.uuid)


@pytest.mark.django_db
def test_non_auth_user_can_not_create_share_ticket(ticket_factory, client):
    ticket = ticket_factory()
    url = reverse("create-share")
    response = client.post(url, data={"ticket": ticket.id}, format="json")
    assert response.status_code == 302
    assert not response.content
    assert reverse("login") in response.url


@pytest.mark.django_db
def test_customer_can_not_create_share_ticket(ticket_factory, client, customer_factory):
    customer = customer_factory()
    ticket = ticket_factory(creator=customer)
    url = reverse("create-share")
    client.force_login(customer)
    response = client.post(url, data={"ticket": ticket.id}, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_operator_can_not_create_share_ticket_for_not_linked_customer(
    ticket_factory, client, operator_factory, customer_factory
):
    customer = customer_factory()
    operator = operator_factory()
    ticket = ticket_factory(creator=customer)
    url = reverse("create-share")
    client.force_login(operator)
    response = client.post(url, data={"ticket": ticket.id}, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
@factory.django.mute_signals(signals.pre_save, signals.post_save)
def test_admin_can_create_share(ticket_factory, client, user_factory):
    admin = user_factory(is_staff=True, is_superuser=True)
    ticket = ticket_factory()
    url = reverse("create-share")
    client.force_login(admin)
    response = client.post(url, data={"ticket": ticket.id}, format="json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_delete_share(client, share_factory):
    share: Share = share_factory()
    ticket_id = share.ticket.pk
    operator = share.creator
    customer = share.ticket.customer
    customer.profile.linked_operators.add(operator)
    client.force_login(operator)
    res = client.post(
        reverse("delete-share", kwargs={"pk": ticket_id}),
        format="json",
    )
    assert Share.objects.filter(pk=share.pk).exists() is False


@pytest.mark.django_db
def test_detail_share(client, share_factory):
    share = share_factory()
    res = client.get(reverse("detail-share", kwargs={"pk": share.pk}))
    assert res.status_code == 200
