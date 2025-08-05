# -*- coding: utf-8 -*-
import requests
import json
import logging
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.utils import timezone
from ..models import WhatsAppAccount, WhatsAppMessage, WhatsAppContact

logger = logging.getLogger(__name__)


class WhatsAppAPIService:
    """
    Servico para integrar com a API oficial do WhatsApp Business
    """
    
    BASE_URL = "https://graph.facebook.com/v19.0"
    
    def __init__(self, account: WhatsAppAccount):
        self.account = account
        self.phone_number_id = account.phone_number_id
        self.access_token = account.access_token
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def send_text_message(self, to: str, message: str, reply_to_message_id: str = None) -> Dict[str, Any]:
        """
        Envia mensagem de texto
        
        Args:
            to: Número do destinatário no formato internacional
            message: Texto da mensagem
            reply_to_message_id: ID da mensagem para responder (opcional)
        
        Returns:
            Dict com resposta da API
        """
        url = f"{self.BASE_URL}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        # Adiciona contexto de resposta se fornecido
        if reply_to_message_id:
            payload["context"] = {
                "message_id": reply_to_message_id
            }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Mensagem de texto enviada com sucesso para {to}")
            return {
                'success': True,
                'message_id': result['messages'][0]['id'],
                'data': result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar mensagem de texto: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def send_media_message(self, to: str, media_type: str, media_id: str = None, 
                          media_url: str = None, caption: str = None) -> Dict[str, Any]:
        """
        Envia mensagem de mídia (imagem, documento, audio, video)
        
        Args:
            to: Número do destinatário
            media_type: Tipo de mídia (image, document, audio, video)
            media_id: ID da mídia já carregada (opcional)
            media_url: URL da mídia (opcional)
            caption: Legenda da mídia (opcional)
        """
        url = f"{self.BASE_URL}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": media_type
        }
        
        # Configura mídia baseado no tipo
        media_payload = {}
        if media_id:
            media_payload["id"] = media_id
        elif media_url:
            media_payload["link"] = media_url
        else:
            return {
                'success': False,
                'error': 'media_id ou media_url deve ser fornecido',
                'data': None
            }
        
        # Adiciona caption se fornecido (apenas para image e video)
        if caption and media_type in ['image', 'video']:
            media_payload["caption"] = caption
        
        payload[media_type] = media_payload
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Mensagem de mídia ({media_type}) enviada com sucesso para {to}")
            return {
                'success': True,
                'message_id': result['messages'][0]['id'],
                'data': result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar mensagem de mídia: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def send_template_message(self, to: str, template_name: str, 
                             language_code: str = "pt_BR", 
                             components: List[Dict] = None) -> Dict[str, Any]:
        """
        Envia mensagem de template
        
        Args:
            to: Número do destinatário
            template_name: Nome do template aprovado
            language_code: Código do idioma
            components: Componentes do template (parâmetros, botões, etc.)
        """
        url = f"{self.BASE_URL}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        if components:
            payload["template"]["components"] = components
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Template '{template_name}' enviado com sucesso para {to}")
            return {
                'success': True,
                'message_id': result['messages'][0]['id'],
                'data': result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar template: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def upload_media(self, file_path: str, media_type: str) -> Dict[str, Any]:
        """
        Faz upload de mídia para o WhatsApp
        
        Args:
            file_path: Caminho para o arquivo
            media_type: Tipo de mídia (image, document, audio, video)
        """
        url = f"{self.BASE_URL}/{self.phone_number_id}/media"
        
        try:
            with open(file_path, 'rb') as file:
                files = {
                    'file': (file_path, file, self._get_mime_type(media_type)),
                    'type': (None, media_type),
                    'messaging_product': (None, 'whatsapp')
                }
                
                headers = {
                    'Authorization': f'Bearer {self.access_token}'
                }
                
                response = requests.post(url, headers=headers, files=files, timeout=60)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Mídia carregada com sucesso: {result['id']}")
                return {
                    'success': True,
                    'media_id': result['id'],
                    'data': result
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao fazer upload de mídia: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': 'Arquivo não encontrado',
                'data': None
            }
    
    def get_media_url(self, media_id: str) -> Dict[str, Any]:
        """
        Obtém URL de download da mídia
        """
        url = f"{self.BASE_URL}/{media_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return {
                'success': True,
                'url': result['url'],
                'mime_type': result.get('mime_type'),
                'file_size': result.get('file_size'),
                'data': result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter URL da mídia: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def download_media(self, media_url: str, file_path: str) -> bool:
        """
        Baixa mídia do WhatsApp
        """
        try:
            response = requests.get(media_url, headers=self.headers, timeout=60, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            logger.info(f"Mídia baixada com sucesso: {file_path}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao baixar mídia: {e}")
            return False
    
    def mark_message_as_read(self, message_id: str) -> bool:
        """
        Marca mensagem como lida
        """
        url = f"{self.BASE_URL}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Mensagem {message_id} marcada como lida")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao marcar mensagem como lida: {e}")
            return False
    
    def get_business_profile(self) -> Dict[str, Any]:
        """
        Obtém perfil de negócio
        """
        url = f"{self.BASE_URL}/{self.phone_number_id}"
        params = {'fields': 'verified_name,display_phone_number,quality_rating'}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return {
                'success': True,
                'data': result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter perfil de negócio: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def _get_mime_type(self, media_type: str) -> str:
        """
        Retorna MIME type baseado no tipo de mídia
        """
        mime_types = {
            'image': 'image/jpeg',
            'document': 'application/pdf',
            'audio': 'audio/mpeg',
            'video': 'video/mp4'
        }
        return mime_types.get(media_type, 'application/octet-stream')
    
    @staticmethod
    def verify_webhook(token: str, verify_token: str) -> bool:
        """
        Verifica token do webhook
        """
        return token == verify_token
    
    @staticmethod
    def parse_webhook_payload(payload: Dict) -> Dict[str, Any]:
        """
        Processa payload do webhook
        """
        try:
            entry = payload.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            
            # Mensagens recebidas
            messages = value.get('messages', [])
            # Status de mensagens
            statuses = value.get('statuses', [])
            # Informações do contato
            contacts = value.get('contacts', [])
            
            return {
                'messages': messages,
                'statuses': statuses,
                'contacts': contacts,
                'metadata': value.get('metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar payload do webhook: {e}")
            return {
                'messages': [],
                'statuses': [],
                'contacts': [],
                'metadata': {}
            }


class WhatsAppWebhookProcessor:
    """
    Processador de webhooks do WhatsApp
    """
    
    def __init__(self, account: WhatsAppAccount):
        self.account = account
    
    async def process_webhook(self, payload: Dict) -> bool:
        """
        Processa webhook recebido
        """
        try:
            data = WhatsAppAPIService.parse_webhook_payload(payload)
            
            # Processa mensagens recebidas
            for message_data in data['messages']:
                await self._process_inbound_message(message_data, data['contacts'])
            
            # Processa updates de status
            for status_data in data['statuses']:
                await self._process_status_update(status_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {e}")
            return False
    
    async def _process_inbound_message(self, message_data: Dict, contacts_data: List[Dict]):
        """
        Processa mensagem recebida
        """
        from django.db import sync_to_async
        
        wamid = message_data['id']
        from_number = message_data['from']
        timestamp = timezone.datetime.fromtimestamp(
            int(message_data['timestamp']), 
            timezone.get_current_timezone()
        )
        
        # Encontra ou cria contato
        contact = await self._get_or_create_contact(from_number, contacts_data)
        
        # Verifica se mensagem já existe
        message_exists = await sync_to_async(
            WhatsAppMessage.objects.filter(wamid=wamid).exists
        )()
        
        if message_exists:
            logger.info(f"Mensagem {wamid} já processada")
            return
        
        # Extrai conteúdo baseado no tipo
        message_type, content, media_data = self._extract_message_content(message_data)
        
        # Salva mensagem no banco
        message = await sync_to_async(WhatsAppMessage.objects.create)(
            wamid=wamid,
            account=self.account,
            contact=contact,
            direction='inbound',
            message_type=message_type,
            content=content,
            timestamp=timestamp,
            status='delivered',
            media_id=media_data.get('id', ''),
            media_filename=media_data.get('filename', ''),
            media_mimetype=media_data.get('mime_type', ''),
            context_data=message_data.get('context', {})
        )
        
        # Notifica via WebSocket
        await self._notify_new_message(message)
        
        logger.info(f"Mensagem inbound processada: {wamid}")
    
    async def _process_status_update(self, status_data: Dict):
        """
        Processa atualização de status de mensagem
        """
        from django.db import sync_to_async
        
        wamid = status_data['id']
        status = status_data['status']
        timestamp = timezone.datetime.fromtimestamp(
            int(status_data['timestamp']),
            timezone.get_current_timezone()
        )
        
        try:
            message = await sync_to_async(WhatsAppMessage.objects.get)(wamid=wamid)
            
            # Atualiza status
            message.status = status
            if status == 'delivered':
                message.delivered_at = timestamp
            elif status == 'read':
                message.read_at = timestamp
            
            await sync_to_async(message.save)()
            
            # Notifica via WebSocket
            await self._notify_status_update(message)
            
            logger.info(f"Status da mensagem {wamid} atualizado para {status}")
            
        except WhatsAppMessage.DoesNotExist:
            logger.warning(f"Mensagem {wamid} não encontrada para atualização de status")
    
    async def _get_or_create_contact(self, phone_number: str, contacts_data: List[Dict]):
        """
        Encontra ou cria contato
        """
        from django.db import sync_to_async
        
        # Busca informações do contato nos dados do webhook
        contact_info = {}
        for contact_data in contacts_data:
            if contact_data.get('wa_id') == phone_number:
                contact_info = contact_data
                break
        
        # Tenta encontrar contato existente
        try:
            contact = await sync_to_async(WhatsAppContact.objects.get)(
                account=self.account,
                phone_number=f"+{phone_number}"
            )
            
            # Atualiza informações se necessário
            if contact_info.get('profile', {}).get('name'):
                contact.profile_name = contact_info['profile']['name']
                await sync_to_async(contact.save)()
            
            return contact
            
        except WhatsAppContact.DoesNotExist:
            # Cria novo contato
            contact = await sync_to_async(WhatsAppContact.objects.create)(
                account=self.account,
                phone_number=f"+{phone_number}",
                profile_name=contact_info.get('profile', {}).get('name', '')
            )
            
            logger.info(f"Novo contato criado: {phone_number}")
            return contact
    
    def _extract_message_content(self, message_data: Dict) -> tuple:
        """
        Extrai conteúdo da mensagem baseado no tipo
        """
        message_type = message_data['type']
        content = ''
        media_data = {}
        
        if message_type == 'text':
            content = message_data['text']['body']
        elif message_type == 'image':
            media_data = message_data['image']
            content = media_data.get('caption', '')
        elif message_type == 'document':
            media_data = message_data['document']
            content = media_data.get('caption', media_data.get('filename', ''))
        elif message_type == 'audio':
            media_data = message_data['audio']
        elif message_type == 'video':
            media_data = message_data['video']
            content = media_data.get('caption', '')
        elif message_type == 'sticker':
            media_data = message_data['sticker']
        elif message_type == 'location':
            location = message_data['location']
            content = f"Lat: {location['latitude']}, Lng: {location['longitude']}"
            if location.get('name'):
                content = f"{location['name']} - {content}"
        elif message_type == 'contacts':
            contacts = message_data['contacts']
            content = json.dumps(contacts)
        
        return message_type, content, media_data
    
    async def _notify_new_message(self, message):
        """
        Notifica nova mensagem via WebSocket
        """
        from channels.layers import get_channel_layer
        from django.db import sync_to_async
        
        channel_layer = get_channel_layer()
        if channel_layer:
            # Serializa mensagem
            message_data = {
                'id': message.id,
                'wamid': message.wamid,
                'contact_id': message.contact.id,
                'contact_name': message.contact.display_name,
                'direction': message.direction,
                'message_type': message.message_type,
                'content': message.get_display_content(),
                'status': message.status,
                'timestamp': message.timestamp.isoformat()
            }
            
            # Notifica sala da conta
            await channel_layer.group_send(
                f'whatsapp_account_{message.account.id}',
                {
                    'type': 'message_received',
                    'message': message_data
                }
            )
            
            # Notifica sala do chat específico
            await channel_layer.group_send(
                f'chat_contact_{message.contact.id}',
                {
                    'type': 'new_message',
                    'message': message_data
                }
            )
    
    async def _notify_status_update(self, message):
        """
        Notifica atualização de status via WebSocket
        """
        from channels.layers import get_channel_layer
        
        channel_layer = get_channel_layer()
        if channel_layer:
            await channel_layer.group_send(
                f'whatsapp_account_{message.account.id}',
                {
                    'type': 'message_status_update',
                    'message_id': message.id,
                    'status': message.status,
                    'timestamp': message.read_at.isoformat() if message.read_at else message.delivered_at.isoformat() if message.delivered_at else None
                }
            )