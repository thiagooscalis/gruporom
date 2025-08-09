# -*- coding: utf-8 -*-
"""
WebSocket consumers for WhatsApp functionality.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class WhatsAppComercialConsumer(AsyncWebsocketConsumer):
    """
    Consumer para atualizações em tempo real da área comercial do WhatsApp
    """
    
    async def connect(self):
        """Conecta o WebSocket"""
        try:
            # Verifica se o usuário está autenticado
            if self.scope["user"].is_anonymous:
                logger.warning("WebSocket: Usuário não autenticado")
                await self.close(code=4001)
                return
            
            # Verifica se o usuário é do grupo Comercial
            is_comercial = await self.is_comercial_user()
            if not is_comercial:
                logger.warning(f"WebSocket: Usuário {self.scope['user'].username} não é do grupo Comercial")
                await self.close(code=4003)
                return
            
            # Adiciona à room group do comercial
            self.room_group_name = 'whatsapp_comercial'
            
            # Adiciona à room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            # Aceita a conexão
            await self.accept()
            logger.info(f"✅ WebSocket conectado com sucesso para usuário {self.scope['user'].username}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar WebSocket: {e}")
            await self.close(code=4000)
    
    async def disconnect(self, close_code):
        """Desconecta o WebSocket"""
        if hasattr(self, 'room_group_name'):
            # Remove da room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        logger.info(f"WebSocket desconectado para usuário {self.scope['user'].username}")
    
    async def receive(self, text_data):
        """Recebe mensagens do WebSocket (não usado neste caso)"""
        pass
    
    # Handlers para diferentes tipos de eventos
    async def conversation_new(self, event):
        """Nova conversa aguardando atendimento"""
        await self.send(text_data=json.dumps({
            'type': 'conversation_new',
            'conversation': event['conversation']
        }))
    
    async def conversation_assigned(self, event):
        """Conversa foi atribuída a um atendente"""
        await self.send(text_data=json.dumps({
            'type': 'conversation_assigned', 
            'conversation': event['conversation']
        }))
    
    async def conversation_updated(self, event):
        """Conversa foi atualizada (nova mensagem, status, etc.)"""
        await self.send(text_data=json.dumps({
            'type': 'conversation_updated',
            'conversation': event['conversation']
        }))
    
    async def message_received(self, event):
        """Nova mensagem recebida em uma conversa"""
        await self.send(text_data=json.dumps({
            'type': 'message_received',
            'message': event['message'],
            'conversation_id': event['conversation_id']
        }))
    
    async def pending_count_update(self, event):
        """Atualiza contador de conversas pendentes"""
        await self.send(text_data=json.dumps({
            'type': 'pending_count_update',
            'count': event['count']
        }))
    
    @database_sync_to_async
    def is_comercial_user(self):
        """Verifica se o usuário pertence ao grupo Comercial"""
        return self.scope["user"].groups.filter(name='Comercial').exists()