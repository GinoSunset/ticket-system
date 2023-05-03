import uuid

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models


class Share(models.Model):
    class Meta:
        verbose_name = "Ссылка на заявку"
        verbose_name_plural = "Ссылки на заявки"
        ordering = ["-created_at"]

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    ticket = models.OneToOneField(
        "ticket.Ticket", on_delete=models.CASCADE, related_name="share"
    )
    creator = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="shares"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # TODO: rename share to resolve func
    def get_absolute_url(self):
        return f"{settings.PROTOCOL}://{Site.objects.get_current()}/share/{self.uuid}"
