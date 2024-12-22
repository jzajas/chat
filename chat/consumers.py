import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):

    connected_users = {}  # Store room-wise connected users

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope['user']

        # Initialize room in connected_users if it doesn't exist
        if self.room_group_name not in self.connected_users:
            self.connected_users[self.room_group_name] = set()

        # Add user to room
        if self.user.is_authenticated:
            self.connected_users[self.room_group_name].add(self.user.username)

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        if self.user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': f'{self.user.username} joined the chat',
                    'username': 'System',
                    'timestamp': timezone.now().isoformat()
                }
            )


    async def disconnect(self, close_code):
        # Remove user from room
        if self.user.is_authenticated:
            self.connected_users[self.room_group_name].discard(self.user.username)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': f'{self.user.username} left the chat',
                    'username': 'System',
                    'timestamp': timezone.now().isoformat()
                }
            )

        await self.update_user_list()


        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def update_user_list(self):
        """Send updated user list to all clients in the room"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_list_update',
                'users': list(self.connected_users[self.room_group_name]),
                'count': len(self.connected_users[self.room_group_name])
            }
        )


    async def user_list_update(self, event):
        """Handler for user list updates"""
        await self.send(text_data=json.dumps({
            'type': 'user_list',
            'users': event['users'],
            'count': event['count']
        }))


    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        if not self.user.is_authenticated:
                    return
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username,
                'timestamp': timezone.now().isoformat()
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))