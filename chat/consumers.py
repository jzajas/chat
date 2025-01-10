import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from chat.models import Room, Message, RoomMember


class ChatConsumer(AsyncWebsocketConsumer):
    connected_users = {} 

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope['user']

        # if not await self.verify_room_access():
        #     await self.close()
        #     return
    
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
                is_system_message=True
            )
            await self.update_user_list()

    @database_sync_to_async
    def get_room(self, room_name):
        room, created = Room.objects.get_or_create(name=room_name)
        if created:
            print(f"Room '{room_name}' was created.")
        return room

    @database_sync_to_async
    def get_chat_history(self):
        messages = Message.objects.filter(room=self.room).order_by('-timestamp')[:50]   
        return [message.to_json() for message in reversed(messages)]

    async def send_chat_history(self):
        history = await self.get_chat_history()
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': history
        }))

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            self.connected_users[self.room_group_name].discard(self.user.username)
            
            await self.save_and_send_message(
                "System",
                f"{self.user.username} left the chat",
                is_system_message=True
            )
            await self.update_user_list()

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    @database_sync_to_async
    def save_message(self, username, message_content, is_system_message=False):
        # sender = None if is_system_message else self.user
        sender = self.user
        message = Message.objects.create(
            room=self.room,
            sender=sender,
            content=message_content
        )
        return message.to_json()

    async def save_and_send_message(self, username, message_content, is_system_message=False):
        message_data = await self.save_message(username, message_content, is_system_message)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_data['content'],
                'username': username,
                'timestamp': message_data['timestamp'],
                'message_id': message_data['id']
            }
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        if not self.user.is_authenticated:
            return

        await self.save_and_send_message(self.user.username, message)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp'],
            'message_id': event.get('message_id')
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