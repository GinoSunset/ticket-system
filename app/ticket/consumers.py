import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer

# from django.contrib.auth.models import AnonymousUser


class MainTableConsumer(AsyncJsonWebsocketConsumer):
    groups = ["general"]

    async def connect(self):
        await self.accept()
        if self.scope["user"]:  # is not AnonymousUser:
            self.user = self.scope["user"]
            self.user_id = self.user.id

            await self.channel_layer.group_add(
                f"{self.user.id}-message", self.channel_name
            )
            if self.user.is_operator:
                await self.channel_layer.group_add(f"operators", self.channel_name)
                return
            await self.channel_layer.group_add("common", self.channel_name)

    async def send_info_to_user_group(self, event):
        message = event["text"]
        await self.send(text_data=json.dumps(message))
