import json
import asyncio

import pytest
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.template import loader
from ticket.consumers import MainTableConsumer

from users.models import CustomerProfile


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_websocket_ticket(ticket_factory, operator_factory, client):
    user = await database_sync_to_async(operator_factory)()
    communicator = WebsocketCommunicator(MainTableConsumer.as_asgi(), "ws/")
    communicator.scope["user"] = user
    connected, subprotocol = await communicator.connect()
    assert connected
    ticket = await database_sync_to_async(ticket_factory)()
    # Test sending text
    response = await communicator.receive_from()
    assert response
    ticket_html = json.loads(response)["ticket"]
    excepted_html = await sync_to_async(
        loader.get_template("ticket/ticket_row.html").render
    )({"ticket": ticket})
    assert ticket_html == excepted_html
    # Close
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_websocket_not_return_with_user_not_access(
    ticket_factory, user_factory, client, customer_factory
):
    user = await database_sync_to_async(user_factory)()
    customer = await database_sync_to_async(customer_factory)()
    profile = await database_sync_to_async(CustomerProfile.objects.get)(
        user=customer.id
    )
    profile.company = "test"
    await database_sync_to_async(profile.save)()
    communicator = WebsocketCommunicator(MainTableConsumer.as_asgi(), "ws/")
    communicator.scope["user"] = user
    connected, subprotocol = await communicator.connect()
    assert connected
    ticket = await database_sync_to_async(ticket_factory)(customer=customer)

    # Test sending text
    with pytest.raises(asyncio.exceptions.TimeoutError):
        await communicator.receive_from()
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_wb_not_return_to_customer(ticket_factory, customer_factory):
    owner_customer = await database_sync_to_async(customer_factory)()
    customer = await database_sync_to_async(customer_factory)()
    communicator = WebsocketCommunicator(MainTableConsumer.as_asgi(), "ws/")
    communicator.scope["user"] = customer
    connected, subprotocol = await communicator.connect()
    assert connected
    ticket = await database_sync_to_async(ticket_factory)(customer=owner_customer)

    # Test sending text
    with pytest.raises(asyncio.exceptions.TimeoutError):
        await communicator.receive_from()
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_wb_return_to_customer(ticket_factory, customer_factory):
    owner_customer = await database_sync_to_async(customer_factory)()
    communicator = WebsocketCommunicator(MainTableConsumer.as_asgi(), "ws/")
    communicator.scope["user"] = owner_customer
    connected, subprotocol = await communicator.connect()
    assert connected
    ticket = await database_sync_to_async(ticket_factory)(customer=owner_customer)

    # Test sending text
    text = await communicator.receive_from()
    assert text
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_wb_not_return_to_contractor(ticket_factory, contractor_factory):
    owner_contractor = await database_sync_to_async(contractor_factory)()
    contractor = await database_sync_to_async(contractor_factory)()
    communicator = WebsocketCommunicator(MainTableConsumer.as_asgi(), "ws/")
    communicator.scope["user"] = contractor
    connected, subprotocol = await communicator.connect()
    assert connected
    ticket = await database_sync_to_async(ticket_factory)(contractor=owner_contractor)

    # Test sending text
    with pytest.raises(asyncio.exceptions.TimeoutError):
        await communicator.receive_from()
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_wb_return_to_contractor(ticket_factory, contractor_factory):
    owner_contractor = await database_sync_to_async(contractor_factory)()
    communicator = WebsocketCommunicator(MainTableConsumer.as_asgi(), "ws/")
    communicator.scope["user"] = owner_contractor
    connected, subprotocol = await communicator.connect()
    assert connected
    ticket = await database_sync_to_async(ticket_factory)(contractor=owner_contractor)

    # Test sending text
    assert await communicator.receive_from()
    await communicator.disconnect()
