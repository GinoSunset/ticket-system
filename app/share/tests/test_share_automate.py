import pytest
from additionally.models import Dictionary
from users.models import CustomerProfile
from share.models import Share
from share.logics import processing_share

import factory
from django.db.models import signals
from django.urls import reverse


@pytest.mark.django_db
def test_create_share_after_ticket_to_work(ticket_factory, user_factory):
    status = Dictionary.get_status_ticket("new")
    status_work = Dictionary.get_status_ticket("work")
    ticket = ticket_factory(status=status)
    assert not Share.objects.filter(ticket=ticket).exists()
    ticket.status = status_work
    processing_share(ticket, user_factory())
    assert ticket.share

@pytest.mark.django_db
    user = user_factory()
    Share.objects.create(ticket=ticket, creator=user)
    processing_share(ticket, user=user)
    assert not Share.objects.filter(ticket=ticket).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status_code, is_exists_share , created_share",
    (
        ("new", False, False),
        ("done", False, True),
        ("cancel", False, True),
        ("work", True, False),
    ),
)
@factory.django.mute_signals(signals.pre_save, signals.post_save)
def test_remove_share_after_save_done_status(
    operator_factory,
    ticket_factory,
    client,
    share_factory,
    customer_factory,
    status_code,
    is_exists_share,
    created_share,
):
    user = operator_factory()
    customer = customer_factory()
    cp = CustomerProfile.objects.create(user=customer)
    user.customers.add(cp)
    ticket = ticket_factory(creator=user, customer=customer)
    user.customers.add(ticket.customer.profile)
    if created_share:
        share_factory(ticket=ticket)
    client.force_login(user=user)
    res = client.post(
        reverse("ticket-update", kwargs={"pk": ticket.pk}),
        data={
            "status": Dictionary.get_status_ticket(status_code).pk,
            "description": ticket.description,
            "customer": ticket.customer.pk,
        },
    )
    assert Share.objects.filter(ticket=ticket).exists() is is_exists_share