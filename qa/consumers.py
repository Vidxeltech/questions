import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ScreenConsumer(AsyncWebsocketConsumer):
    group_name = "screens"

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def broadcast_refresh(self, event):
        await self.send(text_data=json.dumps({
            "type": "refresh",
            "reason": event.get("reason", "update"),
        }))

class ModerationConsumer(AsyncWebsocketConsumer):
    group_name = "moderators"

    async def connect(self):
        # auth check: only staff can connect
        user = self.scope.get("user")
        if not user or not user.is_authenticated or not user.is_staff:
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def broadcast_refresh(self, event):
        await self.send(text_data=json.dumps({
            "type": "refresh",
            "reason": event.get("reason", "update"),
        }))
