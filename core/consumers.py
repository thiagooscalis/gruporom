# -*- coding: utf-8 -*-
import json
import logging
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from .models import WhatsAppAccount, WhatsAppContact, WhatsAppMessage

logger = logging.getLogger(__name__)


class WhatsAppConsumer(AsyncWebsocketConsumer):
    """
    Consumer para WebSocket da conta WhatsApp
    Gerencia conexões em tempo real para uma conta específica
    """
    
    async def connect(self):
        # Verifica autenticação
        if isinstance(self.scope['user'], AnonymousUser):
            await self.close()
            return
        
        self.account_id = self.scope['url_route']['kwargs']['account_id']
        self.room_group_name = f'whatsapp_account_{self.account_id}'
        
        # Verifica se o usuário tem acesso à conta
        has_access = await self.check_account_access()
        if not has_access:
            await self.close()
            return
        
        # Adiciona à sala da conta
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Envia status inicial
        await self.send_account_status()
        
        logger.info(f"WebSocket conectado para conta {self.account_id} pelo usuário {self.scope['user'].username}")
    
    async def disconnect(self, close_code):
        # Remove da sala da conta
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"WebSocket desconectado da conta {self.account_id}")
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'send_message':
                await self.handle_send_message(data)
            elif message_type == 'mark_read':
                await self.handle_mark_read(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            else:
                logger.warning(f"Tipo de mensagem não reconhecido: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Erro ao decodificar JSON do WebSocket")
        except Exception as e:
            logger.error(f"Erro no WebSocket: {e}")
    
    async def handle_send_message(self, data):
        """
        Processa envio de mensagem
        """
        contact_id = data.get('contact_id')
        content = data.get('content', '')
        message_type = data.get('message_type', 'text')
        
        if not contact_id or not content:
            return
        
        try:
            # Salva mensagem no banco
            message = await self.save_outbound_message(
                contact_id=contact_id,
                content=content,
                message_type=message_type
            )
            
            if message:
                # Envia via API do WhatsApp (implementar)
                success = await self.send_to_whatsapp_api(message)
                
                if success:
                    # Notifica todos os clientes conectados
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'message_sent',
                            'message': await self.serialize_message(message)
                        }
                    )
                else:
                    # Marca como falhou
                    await self.mark_message_failed(message.id)
                    
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
    
    async def handle_mark_read(self, data):
        """
        Marca mensagens como lidas
        """
        message_ids = data.get('message_ids', [])
        
        for message_id in message_ids:
            await self.mark_message_read(message_id)
    
    async def handle_typing(self, data):
        """
        Propága status de digitação
        """
        contact_id = data.get('contact_id')
        is_typing = data.get('is_typing', False)
        
        # Notifica outros clientes sobre status de digitação
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_status',
                'contact_id': contact_id,
                'is_typing': is_typing,
                'user': self.scope['user'].username
            }
        )
    
    # Métodos para recebimento de eventos do grupo
    async def message_received(self, event):
        """
        Envia mensagem recebida para o WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'message_received',
            'message': event['message']
        }))
    
    async def message_sent(self, event):
        """
        Envia confirmação de mensagem enviada
        """
        await self.send(text_data=json.dumps({
            'type': 'message_sent',
            'message': event['message']
        }))
    
    async def message_status_update(self, event):
        """
        Envia atualização de status da mensagem
        """
        await self.send(text_data=json.dumps({
            'type': 'message_status_update',
            'message_id': event['message_id'],
            'status': event['status'],
            'timestamp': event.get('timestamp')
        }))
    
    async def typing_status(self, event):
        """
        Envia status de digitação
        """
        # Não envia de volta para o próprio usuário
        if event.get('user') != self.scope['user'].username:
            await self.send(text_data=json.dumps({
                'type': 'typing_status',
                'contact_id': event['contact_id'],
                'is_typing': event['is_typing']
            }))
    
    # Métodos de banco de dados (async)
    @database_sync_to_async
    def check_account_access(self):
        """
        Verifica se o usuário tem acesso à conta
        """
        try:
            account = WhatsAppAccount.objects.get(id=self.account_id)
            # Por enquanto, verifica apenas se a conta existe e está ativa
            # TODO: Implementar permissões mais granulares
            return account.is_active
        except WhatsAppAccount.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_outbound_message(self, contact_id, content, message_type='text'):
        """
        Salva mensagem de saída no banco
        """
        try:
            contact = WhatsAppContact.objects.get(id=contact_id)
            account = WhatsAppAccount.objects.get(id=self.account_id)
            
            message = WhatsAppMessage.objects.create(
                account=account,
                contact=contact,
                direction='outbound',
                message_type=message_type,
                content=content,
                status='pending',
                sent_by=self.scope['user'],
                timestamp=timezone.now()
            )
            
            return message
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem: {e}")
            return None
    
    @database_sync_to_async
    def serialize_message(self, message):
        """
        Serializa mensagem para JSON
        """
        return {
            'id': message.id,
            'wamid': message.wamid,
            'contact_id': message.contact.id,
            'contact_name': message.contact.display_name,
            'direction': message.direction,
            'message_type': message.message_type,
            'content': message.get_display_content(),
            'status': message.status,
            'timestamp': message.timestamp.isoformat(),
            'sent_by': message.sent_by.username if message.sent_by else None
        }
    
    @database_sync_to_async
    def mark_message_read(self, message_id):
        """
        Marca mensagem como lida
        """
        try:
            message = WhatsAppMessage.objects.get(id=message_id)
            message.mark_as_read()
        except WhatsAppMessage.DoesNotExist:
            pass
    
    @database_sync_to_async
    def mark_message_failed(self, message_id):
        """
        Marca mensagem como falhou
        """
        try:
            message = WhatsAppMessage.objects.get(id=message_id)
            message.status = 'failed'
            message.save(update_fields=['status', 'atualizado_em'])
        except WhatsAppMessage.DoesNotExist:
            pass
    
    async def send_account_status(self):
        """
        Envia status inicial da conta
        """
        account_info = await self.get_account_info()
        await self.send(text_data=json.dumps({
            'type': 'account_status',
            'account': account_info
        }))
    
    @database_sync_to_async
    def get_account_info(self):
        """
        Obtém informações da conta
        """
        try:
            account = WhatsAppAccount.objects.get(id=self.account_id)
            return {
                'id': account.id,
                'name': account.name,
                'phone_number': account.display_phone,
                'status': account.status,
                'is_active': account.is_active
            }
        except WhatsAppAccount.DoesNotExist:
            return None
    
    async def send_to_whatsapp_api(self, message):
        """
        Envia mensagem via API do WhatsApp
        TODO: Implementar integração real com a API
        """
        # Por enquanto, simula sucesso
        # Na implementação real, fazer requisição HTTP para a API
        await asyncio.sleep(0.1)  # Simula delay da API
        return True


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer para chat individual com um contato específico
    """
    
    async def connect(self):
        if isinstance(self.scope['user'], AnonymousUser):
            await self.close()
            return
        
        self.contact_id = self.scope['url_route']['kwargs']['contact_id']
        self.room_group_name = f'chat_contact_{self.contact_id}'
        
        # Verifica acesso ao contato
        has_access = await self.check_contact_access()
        if not has_access:
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Envia histórico de mensagens
        await self.send_message_history()
        
        logger.info(f"Chat conectado para contato {self.contact_id}")
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'send_message':
                await self.handle_send_message(data)
            elif message_type == 'load_more':
                await self.handle_load_more(data)
                
        except json.JSONDecodeError:
            logger.error("Erro ao decodificar JSON do chat")
    
    @database_sync_to_async
    def check_contact_access(self):
        """
        Verifica se o usuário tem acesso ao contato
        """
        try:
            contact = WhatsAppContact.objects.get(id=self.contact_id)
            return contact.account.is_active
        except WhatsAppContact.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_message_history(self, limit=50, offset=0):
        """
        Obtém histórico de mensagens
        """
        try:
            contact = WhatsAppContact.objects.get(id=self.contact_id)
            messages = WhatsAppMessage.objects.filter(
                contact=contact
            ).order_by('-timestamp')[offset:offset+limit]
            
            return [{
                'id': msg.id,
                'direction': msg.direction,
                'message_type': msg.message_type,
                'content': msg.get_display_content(),
                'status': msg.status,
                'timestamp': msg.timestamp.isoformat(),
                'sent_by': msg.sent_by.username if msg.sent_by else None
            } for msg in messages]
        except WhatsAppContact.DoesNotExist:
            return []
    
    async def send_message_history(self):
        """
        Envia histórico de mensagens
        """
        messages = await self.get_message_history()
        await self.send(text_data=json.dumps({
            'type': 'message_history',
            'messages': messages
        }))
    
    async def handle_load_more(self, data):
        """
        Carrega mais mensagens
        """
        offset = data.get('offset', 0)
        messages = await self.get_message_history(offset=offset)
        await self.send(text_data=json.dumps({
            'type': 'more_messages',
            'messages': messages
        }))
    
    # Eventos do grupo
    async def new_message(self, event):
        """
        Nova mensagem no chat
        """
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message']
        }))
