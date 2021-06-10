# Main file that handles the chat application
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import pymongo
import datetime
import random

# Initializing database client
db_client = pymongo.MongoClient(
    'mongodb+srv://markis:cmritproject123@cluster0.313vp.mongodb.net/priv?authSource=admin&replicaSet=atlas-fkelf3-shard-0&readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=true')
# Selecting database
db = db_client['privmsg']
col = db["rooms"]


class ChatConsumer(AsyncWebsocketConsumer):

    # Function to handle connections when someone joins 
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # Incrementing connected clients by one
        col.update({'room_name':self.room_name}, {'$inc': {'connected_clients': 1}})
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Getting data to see how many clients are connected
        room = col.find_one({'room_name':self.room_name}, {'_id':0, 'created_at':0, 'messages':0})
        if (room['connected_clients'] == 1):
            # Deleting the room
            col.delete_one({'room_name': self.room_name})
        else:
            # Decrementing connected clients
            col.update({'room_name':self.room_name}, {'$inc': {'connected_clients': -1}})
        # Send message before disconnect
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'leave.message',
                'username': self.username,
            }
        )
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        text_data_json['time'] = datetime.datetime.utcnow()
        # Appending message with username to db
        col.update({'room_name': self.room_name}, {'$push': {'messages' : text_data_json}})
        # Send message to room group depending on type
        if (text_data_json['type'] == 'join.message'):
            # Sending join message
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'join.message',
                    'username': text_data_json['username'],            
                }
            )
        elif (text_data_json['type'] == 'leave.message'):
            # Sending leave message
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'leave.message',
                    'username': text_data_json['username'],            
                }
            )
        elif (text_data_json['type'] == 'chat.message'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat.message',
                    'message':text_data_json['message'],
                    'username': text_data_json['username'],
                    'color': text_data_json['color'],            
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        msg_structure = f"""<div class="pe-2 row my-3 ">
                            <div class="d-flex">
                                <!-- username in box -->
                                <div class="me-3 text-center">
                                    <p id="user-name" style="background-color:{event['color']};" class="user-box m-0 d-flex justify-content-center align-items-center">
                                        
                                    </p>
                                </div>
                                <!-- username and time -->
                                <div class="col h-20">
                                    <div class="row user-info">
                                        <p class="col-1 m-0 ps-3 pe-1 w-auto user-name"></p>
                                        <p class="col m-0 pt-1 px-1 user-time">1</p>
                                    </div>
                                    <!-- text message -->
                                    <div class="row">
                                        <p id="user-text" class="user-texts ps-3 m-0"></p>
                                    </div>
                                </div>
                            </div>
                        </div>"""
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': event['username'],
            'structure': msg_structure,
            'system': False,
        }))

    # Receive message from room group
    async def join_message(self, event):
        # Setting username in instance
        room = col.find_one({'room_name':self.room_name}, {'_id':0, 'created_at':0, 'messages':0})
        self.username = event['username']
        msg_structure = """<div class="pe-2 row my-3 ">
                            <div class="d-flex">
                                <!-- username in box -->
                                <div class="me-3 text-center">
                                    <p id="user-name" class="user-box-PrivMsg m-0 d-flex justify-content-center align-items-center">
                                        Priv<br>Msg
                                    </p>
                                </div>
                                <!-- username and time -->
                                <div class="col h-20">
                                    <div class="row user-info">
                                        <p class="col-1 m-0 ps-3 pe-1 w-auto user-name">PrivMsg</p>
                                        <p class="col m-0 pt-1 px-1 user-time"></p>
                                    </div>
                                    <!-- text message -->
                                    <div class="row">
                                        <p id="user-text" class="user-texts ps-3 m-0"><i>Let's welcome <strong></strong> to the room!<i></p>
                                    </div>
                                </div>
                            </div>
                        </div>"""
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'structure': msg_structure,
            'username': event['username'],
            'system': True,
            "clients": room['connected_clients'],
        }))

    # Receive message from room group
    async def leave_message(self, event):
        room = col.find_one({'room_name':self.room_name}, {'_id':0, 'created_at':0, 'messages':0})
        msg_structure = """<div class="pe-2 row my-3 ">
                            <div class="d-flex">
                                <!-- username in box -->
                                <div class="me-3 text-center">
                                    <p id="user-name" class="user-box-PrivMsg m-0 d-flex justify-content-center align-items-center">
                                        Priv<br>Msg
                                    </p>
                                </div>
                                <!-- username and time -->
                                <div class="col h-20">
                                    <div class="row user-info">
                                        <p class="col-1 m-0 ps-3 pe-1 w-auto user-name">PrivMsg</p>
                                        <p class="col m-0 pt-1 px-1 user-time"></p>
                                    </div>
                                    <!-- text message -->
                                    <div class="row">
                                        <p id="user-text" class="user-texts ps-3 m-0"><i>Bye we'll miss you <strong></strong>!<i></p>
                                    </div>
                                </div>
                            </div>
                        </div>"""
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'structure': msg_structure,
            'username': self.username,
            'system': True,
            "clients": room['connected_clients'],
        }))
