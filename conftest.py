from pytest_factoryboy import register
from ticket.factory import TicketFactory
from users.factory import UserFactory

register(TicketFactory)
register(UserFactory)
