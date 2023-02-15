from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.conf import settings

from ticket.models import Ticket

User = get_user_model()


class Notification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.message}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    @classmethod
    def create_notify_update_ticket(cls, update_field, ticket: Ticket):
        template_dict = {
            "contractor": Notification.create_notify_update_customer,
        }
        for field in update_field:
            create_func = template_dict.get(field)
            if create_func:
                create_func(ticket)

    @classmethod
    def create_notify_update_customer(cls, ticket: Ticket):
        link = f"{settings.PROTOCOL}://{Site.objects.get_current()}{ticket.get_absolute_url()}"
        message = (
            f"Вы назначены исполнителем заявки №{ticket.id}.\n"
            "Информация о заявке:\n"
            f"адрес: {ticket.address}\n"
            "описание:\n"
            f"{ticket.description} \n"
            f"Перейти к заявке: {link}"
        )
        user = ticket.contractor
        cls.objects.create(user=user, message=message)
