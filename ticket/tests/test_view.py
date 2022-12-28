import pytest
from pytest_django.asserts import assertQuerysetEqual
from django.urls import reverse
from ticket.models import Ticket


@pytest.mark.django_db
def test_user_see_self_ticket(ticket_factory, user_factory, client):
    user1 = user_factory()
    user1.save()
    user_another = user_factory()
    user_another.save()
    ticket: Ticket = ticket_factory(creator=user1)
    ticket.save()
    ticket_another = ticket_factory(creator=user_another)
    ticket_another.save()
    client.force_login(user=user1)
    response = client.get(reverse("tickets-list"))
    assertQuerysetEqual(
        response.context_data["ticket_list"], Ticket.objects.filter(creator=user1)
    )


@pytest.mark.django_db
def test_admin_see_all_ticket(ticket_factory, user_factory, client):
    user1 = user_factory()
    user1.save()
    admin_user = user_factory(is_staff=True)
    admin_user.save()
    user_another = user_factory()
    user_another.save()
    ticket: Ticket = ticket_factory(creator=user1)
    ticket.save()
    ticket_another = ticket_factory(creator=user_another)
    ticket_another.save()
    client.force_login(user=admin_user)
    response = client.get(reverse("tickets-list"))
    assert list(response.context_data["ticket_list"]), list(Ticket.objects.all())
