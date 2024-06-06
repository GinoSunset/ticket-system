import pytest
import factory
from ticket import signals
from storage.reserve import reserve_component
from storage.models import Component


@factory.django.mute_signals(signals.post_save)
@pytest.mark.django_db
def test_ticket_has_components(
    ticket_factory, free_component, customer_profile_factory
):
    ticket = ticket_factory()
    customer_profile_factory(user=ticket.customer)
    reserve_component(free_component.component_type, ticket)
    free_component.refresh_from_db()
    assert free_component.ticket == ticket


@factory.django.mute_signals(signals.post_save)
@pytest.mark.django_db
def test_ticket_reserve_phantom_component(
    ticket_factory, customer_profile_factory, component_type
):
    ticket = ticket_factory()
    customer_profile_factory(user=ticket.customer)
    reserve_component(component_type, ticket)
    assert Component.objects.filter(component_type=component_type).first().is_phantom


@pytest.mark.django_db
def test_components_from_ticket_to_archive(
    redis,
    ticket_factory,
    free_component,
    status_done,
):
    ticket = ticket_factory()
    reserve_component(free_component.component_type, ticket)

    ticket.status = status_done
    ticket.save()

    free_component.refresh_from_db()
    assert free_component.is_archive


def test_check_if_has_delivery():
    """Проверяет что после создания доставки фантомные
    компоненты заменяться на те которые в доставке и они
     зарезервируют"""
    assert False


# TODO: спросить про ранжирование при резервировании
