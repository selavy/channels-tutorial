from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
import channels.auth
import json


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Channel join:
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Channel unsub:
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    # message from websocket from UI
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
            }
        )

    # message from group:
    async def chat_message(self, event):
        message = event['message']

        # # XXX: this is an example of how to get the current user:
        # # if the user hasn't been loaded yet, then it will return an instance
        # # of AnonymousUser():
        # user = self.scope.get('user', 'UNKNOWN')
        # user = await channels.auth.get_user(self.scope)

        # send on websocket to UI
        await self.send(text_data=json.dumps({
            'message': message,
        }))
