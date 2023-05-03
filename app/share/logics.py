from additionally.models import Dictionary
from .models import Share
from users.models import User


def processing_share(ticket, user: User):
    status_completed = Dictionary.objects.filter(code__in=["done", "cancel"])
    status_to_create_share = Dictionary.objects.filter(code__in=["work"])
    if ticket.status in status_to_create_share:
        create_share(ticket, user)
        return
    if ticket.status in status_completed:
        remove_share(ticket)


def create_share(ticket, user: User):
    if not hasattr(ticket, "share"):
        Share.objects.create(ticket=ticket, creator=user)


def remove_share(ticket):
    if hasattr(ticket, "share"):
        ticket.share.delete()
