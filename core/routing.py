# -*- coding: utf-8 -*-
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/whatsapp/(?P<account_id>\w+)/$', consumers.WhatsAppConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<contact_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
]