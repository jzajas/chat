from django.urls import re_path
from chat.consumers import ChatConsumer


from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
    re_path("" , ChatConsumer.as_asgi()) , 

]