# -*- coding: utf-8 -*-
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # WebSocket para área comercial do WhatsApp (atualizações em tempo real)
    re_path(r'ws/comercial/whatsapp/$', consumers.WhatsAppComercialConsumer.as_asgi()),
]