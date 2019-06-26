from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json


# TODO: convert to async consumer
class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Channel join:
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

        self.accept()

    def disconnect(self, close_code):
        # Channel unsub:
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

    # message from websocket from UI
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
            }
        )

    # message from group:
    def chat_message(self, event):
        message = event['message']

        # send on websocket to UI
        self.send(text_data=json.dumps({
            'message': message,
            # 'user': scope['user'],
        }))
