# Main file that handles the chat application
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import pymongo

# Initializing database client
db_client = pymongo.MongoClient(
    'mongodb+srv://markis:cmritproject123@cluster0.313vp.mongodb.net/priv?authSource=admin&replicaSet=atlas-fkelf3-shard-0&readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=true')
# Selecting database
db = db_client['privmsg']
col = db["rooms"]


class ChatConsumer(AsyncWebsocketConsumer):

    # Function to handle connections when someone joins or leaves group
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        col.insert(text_data_json)
        message = text_data_json['message']
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
