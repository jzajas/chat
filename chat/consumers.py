import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # adding name to database
        # Clients.objects.create(channel_name=self.channel_name)

        # self.username = await get_name()


        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Remove name from database
        # Clients.objects.filter(channel_name=self.channel_name).delete()


    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message, "username" : username}
        )

        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #         {
        #             "type": "chat.message",
        #             "room_id": room_id,
        #             "username": self.scope["user"].username,
        #             "message": message,
        #         }
        # )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        
        # await self.send_json(
        # {
        #     "msg_type": settings.MSG_TYPE_MESSAGE,
        #     "room": event["room_id"],
        #     "username": event["username"],
        #     "message": event["message"],
        # },
        # )

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, "username" : username}))

    
    # @database_sync_to_async
    # def get_name(self):
    #     return User.objects.all()[0].name