from channels.testing import HttpCommunicator

from ticket.consumer import MainTableConsumer


def test_notify_when_create_new_ticket(ticket_factory):
    communicator = HttpCommunicator(MainTableConsumer.as_asgi(), "GET", "/")
    t = ticket_factory()
    res = communicator.get_response()
    assert False
