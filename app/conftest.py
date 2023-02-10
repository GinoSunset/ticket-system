from pytest_factoryboy import register
from ticket.factory import TicketFactory
from users.factory import UserFactory, CustomerFactory, OperatorFactory
from notifications.factory import NotificationFactory

register(TicketFactory)
register(UserFactory)
register(CustomerFactory)
register(OperatorFactory)
register(NotificationFactory)
