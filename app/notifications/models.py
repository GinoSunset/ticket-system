from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.conf import settings
from django.template import loader

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
            "contractor": Notification.create_notify_update_contractor,
        }
        for field in update_field:
            create_func = template_dict.get(field)
            if create_func:
                create_func(ticket)

    @classmethod
    def create_notify_update_contractor(cls, ticket: Ticket):
        link = f"{settings.PROTOCOL}://{Site.objects.get_current()}{ticket.get_absolute_url()}"
        message = loader.get_template("notifications/notify_set_contractor.txt").render(
            {"ticket": ticket, "link": link}
        )
        user = ticket.contractor
        cls.objects.create(user=user, message=message)
