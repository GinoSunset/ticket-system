from .models import Notification
from ticket.models import Ticket
from users.models import Customer, User


def create_operator_notify_for_create_comment(comment):
    ticket = comment.ticket
    link = ticket.get_external_url()
    message = f"Создан комментарий к заявке #{ticket.pk}.\n\nТекст комментария:\n{comment.text}.\n\nСсылка: {link}"
    for user in get_users_for_create_notify(ticket):
        Notification.objects.create(
            user=user,
            message=message,
            type_notify="ticket_comment",
            ticket=ticket,
            subject=f"Комментарий к заявке #{ticket.pk}",
        )


def get_users_for_create_notify(ticket: Ticket):
    customer: Customer = ticket.customer.get_role_user()
    operator_user = None
    if customer.is_customer:
        operators = customer.get_operators()
        operator_user = User.objects.filter(id__in=operators)
    admins = User.objects.filter(is_staff=True)
    users = operator_user | admins

    return users.distinct()
