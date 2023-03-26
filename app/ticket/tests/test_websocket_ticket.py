import pytest
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from ticket.consumers import MainTableConsumer


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_websocket_ticket(ticket_factory):
    communicator = WebsocketCommunicator(MainTableConsumer.as_asgi(), "ws/")
    connected, subprotocol = await communicator.connect()
    assert connected
    ticket = await database_sync_to_async(ticket_factory)()
    # Test sending text
    response = await communicator.receive_from()
    assert response == ticket.id
    # Close
    await communicator.disconnect()
