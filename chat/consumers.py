import json
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncConsumer, SyncConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from chat.models import Room, Message, RoomMember
from asgiref.sync import async_to_sync
import re

channel_layer_outside = get_channel_layer()

class ChatConsumer(AsyncWebsocketConsumer):
    connected_users = {} 

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope['user']
    
        self.room = await self.get_room(self.room_name)

        if self.room_group_name not in self.connected_users:
            self.connected_users[self.room_group_name] = set()

        if self.user.is_authenticated:
            self.connected_users[self.room_group_name].add(self.user.username)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send_chat_history()

        if self.user.is_authenticated:
            await self.save_and_send_message(
                "System",
                f"{self.user.username} joined the chat",
                
            )
            await self.update_user_list()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            self.connected_users[self.room_group_name].discard(self.user.username)
            
            await self.save_and_send_message(
                "System",
                f"{self.user.username} left the chat",
                
            )
            await self.update_user_list()

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def save_and_send_message(self, username, message_content):
        message_data = await self.save_message(message_content)
        
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type': 'chat_message',
        #         'message': message_data['content'],
        #         'username': username,
        #         'timestamp': message_data['timestamp'],
        #         'message_id': message_data['id']
        #     }
        # )
        await self.channel_layer.send(
        'background-tasks',
        {
            'type': 'message_filter',
            'message': message_data['content'],
            'username': username,
            'timestamp': message_data['timestamp'],
            'message_id': message_data['id'],
            'room_group': self.room_group_name
        }
        )

    @database_sync_to_async
    def save_message(self, message_content):
        message = Message.objects.create(
            room = self.room,
            sender = self.user,
            content = message_content
        )
        return message.to_json()


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        if not self.user.is_authenticated:
            return
        await self.save_and_send_message(self.user.username, message)


    async def chat_message(self, event):

        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event.get('message'),
            'username': event.get('username'),
            'timestamp': event.get('timestamp'),
            'message_id': event.get('message_id')
        }))


    @database_sync_to_async
    def get_room(self, room_name):
        room, created = Room.objects.get_or_create(name=room_name)
        return room

    @database_sync_to_async
    def get_chat_history(self):
        messages = Message.objects.filter(room=self.room).order_by('-timestamp')[:70]   
        return [message.to_json() for message in reversed(messages)]

    async def send_chat_history(self):
        history = await self.get_chat_history()
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': history
        }))


    async def update_user_list(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_list_update',
                'users': list(self.connected_users[self.room_group_name]),
                'count': len(self.connected_users[self.room_group_name])
            }
        )

    async def user_list_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_list',
            'users': event['users'],
            'count': event['count']
        }))
    

class BackgroundTaskConsumer(SyncConsumer):

    def filter_message(self, message):

        bad_words = [
        "kurwa",
        ]
        
        new_message = message
        message_part = message.split(" ")
                        
        for word in message_part:
            word_lower = word.lower()
            if word_lower in bad_words:
                new_message = message.replace(word, "*" * len(word))

        return new_message
    

    def message_filter(self, message):
        room_group_name = message['room_group']
        content = message['message']
        username = message['username']
        timestamp = message.get("timestamp")
        id = message.get("id")

        filtered_content = self.filter_message(content)

        async_to_sync(self.channel_layer.group_send)(
            room_group_name,
            {
                'type': 'chat_message',
                'message': filtered_content,
                'username': username,
                'timestamp': timestamp,
                'message_id': id,
                'room_group': room_group_name
            }
        )
