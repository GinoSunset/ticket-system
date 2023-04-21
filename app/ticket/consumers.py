from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from asgiref.sync import sync_to_async

from django.template import loader
from .models import Ticket
from users.models import User


class MainTableConsumer(AsyncJsonWebsocketConsumer):
    groups = ["general"]

    async def connect(self):
        await self.accept()
        if self.scope["user"] and not self.scope["user"]:  # is not AnonymousUser:
            user: User = self.scope["user"]
            self.user = await database_sync_to_async(user.get_role_user)()
            self.user_id = self.user.pk

            if self.user.is_operator or self.user.is_staff:
                await self.channel_layer.group_add(f"operators", self.channel_name)
                return
            if self.user.is_customer:
                await self.channel_layer.group_add(
                    f"customer_{self.user.pk}", self.channel_name
                )
                return
            if self.user.is_contractor:
                await self.channel_layer.group_add(
                    f"contractor_{self.user.pk}", self.channel_name
                )
                return
            await self.channel_layer.group_add("common", self.channel_name)

    async def send_info_to_user_group(self, event):
        ticket: Ticket = await self.get_ticket_by_id(event["ticket_id"])
        render_ticket = await sync_to_async(
            loader.get_template("ticket/ticket_row.html").render
        )({"ticket": ticket, "user": self.user})
        ticket_json = {
            "ticket": render_ticket,
            "info": {
                "id": ticket.pk,
                "customer": str(ticket.customer),
                "sap": ticket.sap_id,
            },
        }
        await self.send_json(ticket_json)

    async def hello(self, event):
        await self.send_json(event)

    @database_sync_to_async
    def get_ticket_by_id(self, ticket_id):
        ticket = Ticket.objects.get(id=ticket_id)
        return ticket
