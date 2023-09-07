from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/live-streaming/(?P<p_id>[\w-]+)/$', consumers.LiveChatConsumer.as_asgi()),
]