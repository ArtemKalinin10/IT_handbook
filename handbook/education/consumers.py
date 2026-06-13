from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json


class SubmissionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        from education.models import Task

        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close()
            return

        task_id = self.scope['url_route']['kwargs']['task_id']

        task_exists = await database_sync_to_async(
            Task.objects.filter(pk=task_id).exists
        )()

        if not task_exists:
            await self.close()
            return

        self.group_name = f"task_{task_id}_user_{user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def submission_update(self, event):
        await self.send(
            text_data=json.dumps({
                "submission_id": event["submission_id"],
                "status": event["status"],
            })
        )