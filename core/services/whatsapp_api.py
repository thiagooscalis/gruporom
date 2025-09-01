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
        # Mock para ambiente de desenvolvimento
        if settings.DEBUG:
            import uuid
            mock_id = f"wamid.{uuid.uuid4().hex[:20]}"
            logger.info(f"🎭 MOCK: Simulando envio de mensagem de texto para {to}")
            return {
                'messages': [{
                    'id': mock_id
                }],
                'success': True,
                'message_id': mock_id
            }
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
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar mensagem de texto: {e}")
            
            # Tenta extrair mensagem de erro do response se disponível
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    if 'error' in error_data:
                        error_message = error_data['error'].get('message', str(e))
                except:
                    pass
            
            raise Exception(error_message)
    
    def send_media_message(self, to: str, media_type: str, media_id: str = None, 
                          media_url: str = None, caption: str = None, filename: str = None) -> Dict[str, Any]:
        """
        Envia mensagem de mídia (imagem, documento, audio, video)
        
        Args:
            to: Número do destinatário
            media_type: Tipo de mídia (image, document, audio, video)
            media_id: ID da mídia já carregada (opcional)
            media_url: URL da mídia (opcional)
            caption: Legenda da mídia (opcional)
            filename: Nome do arquivo (obrigatório para documents)
        """
        url = f"{self.BASE_URL}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": media_type
        }
        
        # Para documents, adiciona recipient_type conforme documentação oficial
        if media_type == 'document':
            payload["recipient_type"] = "individual"
        
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
        
        # Adiciona caption se fornecido (para image, video e document)
        if caption and media_type in ['image', 'video', 'document']:
            media_payload["caption"] = caption
        
        # Adiciona filename para documents (OBRIGATÓRIO na API do WhatsApp)
        if media_type == 'document' and filename:
            media_payload["filename"] = filename
        
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
            
            # Tenta extrair detalhes do erro
            error_message = str(e)
            error_details = {}
            
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_details = error_data.get('error', {})
                    error_message = error_details.get('message', str(e))
                    
                    logger.error(f"[WHATSAPP API] Status HTTP: {e.response.status_code}")
                    logger.error(f"[WHATSAPP API] Erro detalhado: {error_details}")
                    logger.error(f"[WHATSAPP API] Payload enviado: type={media_type}, url={media_url[:100] if media_url else 'None'}...")
                except:
                    logger.error(f"[WHATSAPP API] Resposta não-JSON: {e.response.text[:500]}")
            
            return {
                'success': False,
                'error': error_message,
                'error_details': error_details,
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
        # Mock para ambiente de desenvolvimento
        if settings.DEBUG:
            import uuid
            mock_id = f"wamid.{uuid.uuid4().hex[:20]}"
            logger.info(f"🎭 MOCK: Simulando envio de template '{template_name}' para {to}")
            return {
                'success': True,
                'message_id': mock_id,
                'data': {
                    'messages': [{
                        'id': mock_id
                    }]
                }
            }
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
    
    def create_message_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria um novo template de mensagem para aprovação
        
        Args:
            template_data: Dados do template conforme API do WhatsApp
        
        Returns:
            Dict com resultado da operação
        """
        url = f"{self.BASE_URL}/{self.account.business_account_id}/message_templates"
        
        try:
            response = requests.post(url, headers=self.headers, json=template_data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Template criado com sucesso: {result.get('id')}")
            return {
                'success': True,
                'template_id': result.get('id'),
                'status': result.get('status'),
                'data': result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao criar template: {e}")
            # URLs e headers removidos por segurança em produção
            
            error_response = {}
            error_details = None
            error_text = ""
            
            try:
                if hasattr(e, 'response') and e.response is not None:
                    # Status code da resposta
                    logger.error(f"Status HTTP: {e.response.status_code}")
                    
                    # Conteúdo da resposta (logs seguros)
                    try:
                        error_text = e.response.text
                        
                        if error_text.strip():
                            try:
                                error_response = e.response.json()
                                error_details = error_response.get('error', {})
                                # Log apenas informações seguras de erro
                                safe_error = {
                                    'message': error_details.get('message', 'Erro desconhecido'),
                                    'type': error_details.get('type'),
                                    'code': error_details.get('code'),
                                    'status': e.response.status_code
                                }
                                logger.error(f"Erro da API WhatsApp: {safe_error}")
                            except json.JSONDecodeError:
                                logger.error("Erro na API WhatsApp (resposta inválida)")
                                error_response = {'error': 'Resposta inválida'}
                        else:
                            logger.error("API WhatsApp retornou resposta vazia")
                            error_response = {'error': 'Resposta vazia'}
                            
                    except Exception:
                        logger.error("Erro ao processar resposta da API WhatsApp")
                        error_response = {'error': 'Erro ao processar resposta'}
                else:
                    logger.error("Nenhuma resposta HTTP disponível")
                    error_response = {'error': 'Sem resposta HTTP'}
                    
            except Exception as parse_error:
                logger.error(f"Erro ao processar resposta: {parse_error}")
                error_response = {'error': f'Erro de parsing: {str(parse_error)}'}
            
            return {
                'success': False,
                'error': str(e),
                'error_details': error_response,
                'error_message': error_details.get('message') if error_details else str(e),
                'error_code': error_details.get('code') if error_details else None,
                'raw_response': error_text,
                'data': None
            }
    
    def submit_template_for_approval(self, template) -> Dict[str, Any]:
        """
        Submete um template local para aprovação na API do WhatsApp
        
        Args:
            template: Instância de WhatsAppTemplate
        
        Returns:
            Dict com resultado da operação
        """
        # Extrai variáveis do template e gera exemplos
        import re
        
        def extract_variables_and_examples(text, custom_examples=None):
            """Extrai variáveis {{n}} e gera exemplos"""
            if not text:
                return None
                
            variables = re.findall(r'\{\{(\d+)\}\}', text)
            if not variables:
                return None
            
            # Exemplos padrão para cada posição de variável
            default_example_values = [
                "João Silva",           # Nome
                "Grupo ROM",            # Empresa
                "12345",               # Código/ID
                "10/01/2025",          # Data
                "14:30",               # Hora
                "São Paulo",           # Cidade
                "R$ 100,00",           # Valor
                "www.gruporom.com",    # URL
                "Produto X",           # Produto
                "50%"                  # Percentual
            ]
            
            examples = []
            for var in sorted(set(variables), key=int):
                var_index = int(var) - 1
                
                # Usa exemplo customizado se fornecido, senão usa padrão
                if custom_examples and str(var) in custom_examples:
                    examples.append(custom_examples[str(var)])
                elif var_index < len(default_example_values):
                    examples.append(default_example_values[var_index])
                else:
                    examples.append(f"Exemplo{var}")
            
            return examples
        
        # Monta a estrutura do template conforme API do WhatsApp
        components = []
        
        # Obtém exemplos customizados do template
        custom_examples = template.variables_examples if hasattr(template, 'variables_examples') and template.variables_examples else None
        
        # Adiciona header se existir
        if template.header_text:
            header_component = {
                "type": "HEADER",
                "format": "TEXT",
                "text": template.header_text
            }
            
            # Adiciona exemplos se houver variáveis no header
            header_examples = extract_variables_and_examples(template.header_text, custom_examples)
            if header_examples:
                header_component["example"] = {
                    "header_text": header_examples
                }
            
            components.append(header_component)
        
        # Adiciona body (obrigatório)
        body_component = {
            "type": "BODY",
            "text": template.body_text
        }
        
        # Adiciona exemplos se houver variáveis no body
        body_examples = extract_variables_and_examples(template.body_text, custom_examples)
        if body_examples:
            body_component["example"] = {
                "body_text": [body_examples]  # API espera array de arrays
            }
        
        components.append(body_component)
        
        # Adiciona footer se existir
        if template.footer_text:
            components.append({
                "type": "FOOTER",
                "text": template.footer_text
            })
        
        # Adiciona botões se configurados
        if template.has_buttons and template.buttons_config:
            # Formata botões corretamente
            formatted_buttons = []
            for button in template.buttons_config:
                if isinstance(button, dict):
                    button_data = {
                        "type": button.get("type", "QUICK_REPLY"),
                        "text": button.get("text", "")
                    }
                    
                    # Adiciona campos específicos por tipo
                    if button.get("type") == "URL":
                        button_data["url"] = button.get("url", "")
                    elif button.get("type") == "PHONE_NUMBER":
                        button_data["phone_number"] = button.get("phone_number", "")
                    
                    formatted_buttons.append(button_data)
            
            if formatted_buttons:
                components.append({
                    "type": "BUTTONS",
                    "buttons": formatted_buttons
                })
        
        # Mapeia o código de idioma para o formato aceito pela API
        language_mapping = {
            'pt_BR': 'pt_BR',
            'en_US': 'en_US',
            'es_ES': 'es',
            'en': 'en',
            'pt': 'pt_BR'
        }
        
        language_code = language_mapping.get(template.language, template.language)
        
        # Monta o payload completo - Formato correto da API v19.0
        template_data = {
            "name": template.name.lower().replace('-', '_'),  # Garante formato correto do nome
            "category": template.category.upper(),
            "language": language_code,
            "components": components
        }
        
        # Adiciona allow_category_change apenas para categorias que permitem
        if template.category.upper() in ['MARKETING', 'UTILITY']:
            template_data["allow_category_change"] = True
        
        # Validações do payload antes de enviar
        validation_errors = []
        
        # Valida nome do template
        if not template_data.get('name'):
            validation_errors.append("Nome do template é obrigatório")
        elif not re.match(r'^[a-z0-9_]+$', template_data['name']):
            validation_errors.append("Nome deve conter apenas letras minúsculas, números e underscore")
        
        # Valida categoria
        valid_categories = ['UTILITY', 'MARKETING', 'AUTHENTICATION']
        if template_data.get('category') not in valid_categories:
            validation_errors.append(f"Categoria deve ser uma de: {', '.join(valid_categories)}")
        
        # Valida idioma
        if not template_data.get('language'):
            validation_errors.append("Idioma é obrigatório")
        
        # Valida business_account_id
        if not self.account.business_account_id:
            validation_errors.append("Business Account ID não configurado na conta")
        elif not str(self.account.business_account_id).isdigit():
            validation_errors.append("Business Account ID deve ser numérico")
        
        # Valida componentes
        if not template_data.get('components') or len(template_data['components']) == 0:
            validation_errors.append("Pelo menos um componente é obrigatório")
        else:
            # Verifica se tem pelo menos um BODY
            has_body = any(comp.get('type') == 'BODY' for comp in template_data['components'])
            if not has_body:
                validation_errors.append("Componente BODY é obrigatório")
        
        if validation_errors:
            error_msg = "Validação falhou: " + "; ".join(validation_errors)
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'error_details': {'validation_errors': validation_errors},
                'data': None
            }
        
        # Log do payload para debug
        logger.info(f"Enviando template para aprovação: {template.name}")
        # URLs e IDs de negócio removidos dos logs por segurança
        # Payload de template removido dos logs por segurança
        
        # Chama a API para criar o template
        result = self.create_message_template(template_data)
        
        # Atualiza o template local com o resultado
        if result['success']:
            template.template_id = result.get('template_id')
            template.status = 'pending'  # Status inicial após submissão
            template.save(update_fields=['template_id', 'status', 'atualizado_em'])
            logger.info(f"Template {template.name} submetido para aprovação com ID: {template.template_id}")
        else:
            # Salva o motivo do erro se houver
            error_details = result.get('error_details', {}).get('error', {})
            error_msg = error_details.get('message', str(result.get('error')))
            
            # Se for erro de template duplicado, adiciona sugestões
            if error_details.get('error_subcode') == 2388024:
                suggestions = [
                    f"{template.name}_v2",
                    f"{template.name}_2025", 
                    f"{template.name}_new",
                    f"{template.name}_{timezone.now().strftime('%m%d')}"
                ]
                error_msg = f"{error_details.get('error_user_msg', error_msg)}. Sugestões de nomes: {', '.join(suggestions)}"
            
            template.rejection_reason = f"Erro ao submeter: {error_msg}"
            template.save(update_fields=['rejection_reason', 'atualizado_em'])
            logger.error(f"Falha ao submeter template {template.name}: {error_msg}")
        
        return result
    
    def get_template_status(self, template_id: str) -> Dict[str, Any]:
        """
        Consulta o status de um template na API
        
        Args:
            template_id: ID do template no WhatsApp
        
        Returns:
            Dict com status e informações do template
        """
        url = f"{self.BASE_URL}/{self.account.business_account_id}/message_templates"
        params = {
            'fields': 'id,name,status,category,language,components,rejected_reason',
            'limit': 1,
            'name': template_id
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            templates = result.get('data', [])
            
            if templates:
                template_info = templates[0]
                return {
                    'success': True,
                    'status': template_info.get('status'),
                    'rejected_reason': template_info.get('rejected_reason'),
                    'data': template_info
                }
            else:
                return {
                    'success': False,
                    'error': 'Template não encontrado',
                    'data': None
                }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar status do template: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def update_template_status(self, template) -> Dict[str, Any]:
        """
        Atualiza o status de um template consultando a API
        
        Args:
            template: Instância de WhatsAppTemplate
        
        Returns:
            Dict com resultado da operação
        """
        if not template.template_id and not template.name:
            return {
                'success': False,
                'error': 'Template não tem ID ou nome para consulta',
                'updated': False
            }
        
        # Tenta buscar pelo nome do template
        result = self.get_template_status(template.name)
        
        if result['success']:
            api_status = result['status'].lower()
            api_rejected_reason = result.get('rejected_reason', '')
            
            # Mapeia status da API para status local
            status_mapping = {
                'approved': 'approved',
                'rejected': 'rejected', 
                'pending': 'pending',
                'disabled': 'disabled',
                'paused': 'disabled'
            }
            
            new_status = status_mapping.get(api_status, 'pending')
            
            # Verifica se houve mudança no status ou motivo de rejeição
            status_changed = new_status != template.status
            reason_changed = (new_status == 'rejected' and 
                            api_rejected_reason != template.rejection_reason)
            
            if status_changed or reason_changed:
                old_status = template.status
                template.status = new_status
                
                # Atualiza motivo de rejeição se aplicável
                if new_status == 'rejected':
                    template.rejection_reason = api_rejected_reason or 'Motivo não especificado'
                elif new_status == 'approved':
                    # Limpa motivo de rejeição se foi aprovado
                    template.rejection_reason = ''
                
                # Salva no banco de dados
                template.save(update_fields=['status', 'rejection_reason', 'atualizado_em'])
                
                logger.info(f"Template {template.name} atualizado: {old_status} → {new_status}")
                
                return {
                    'success': True,
                    'updated': True,
                    'old_status': old_status,
                    'new_status': new_status,
                    'rejection_reason': template.rejection_reason if new_status == 'rejected' else None
                }
            else:
                return {
                    'success': True,
                    'updated': False,
                    'current_status': template.status,
                    'message': 'Status não mudou'
                }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Erro ao consultar API'),
                'updated': False
            }
    
    def delete_template(self, template_name: str) -> Dict[str, Any]:
        """
        Deleta um template da API do WhatsApp
        
        Args:
            template_name: Nome do template
        
        Returns:
            Dict com resultado da operação
        """
        url = f"{self.BASE_URL}/{self.account.business_account_id}/message_templates"
        params = {'name': template_name}
        
        try:
            response = requests.delete(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Template {template_name} deletado com sucesso")
            return {
                'success': True,
                'data': result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao deletar template: {e}")
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
        # Para IDs de teste do simulador, retorna URLs de exemplo
        if media_id.startswith('media_'):
            test_media_urls = {
                'image': {
                    'url': 'https://picsum.photos/800/600',
                    'mime_type': 'image/jpeg',
                    'file_size': 150000
                },
                'audio': {
                    'url': 'https://www.kozco.com/tech/LRMonoPhase4.wav',
                    'mime_type': 'audio/wav',
                    'file_size': 50000
                },
                'video': {
                    'url': 'https://sample-videos.com/zip/10/mp4/SampleVideo_360x240_1mb.mp4',
                    'mime_type': 'video/mp4',
                    'file_size': 1000000
                },
                'document': {
                    'url': 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf',
                    'mime_type': 'application/pdf',
                    'file_size': 100000
                }
            }
            
            # Identifica tipo baseado no ID
            media_type = None
            type_mapping = {
                'img': 'image',      # media_img_* -> image
                'image': 'image',    # media_image_* -> image  
                'audio': 'audio',    # media_audio_* -> audio
                'video': 'video',    # media_video_* -> video
                'doc': 'document'    # media_doc_* -> document
            }
            
            for id_pattern, type_name in type_mapping.items():
                if id_pattern in media_id:
                    media_type = type_name
                    break
            
            if media_type:
                media_info = test_media_urls[media_type]
                logger.info(f"Retornando URL de teste para {media_id}: {media_info['url']}")
                return {
                    'success': True,
                    'url': media_info['url'],
                    'mime_type': media_info['mime_type'],
                    'file_size': media_info['file_size'],
                    'data': media_info
                }
        
        # URL real para IDs de produção
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
    
    def test_api_permissions(self) -> Dict[str, Any]:
        """
        Testa se o access token tem as permissões necessárias
        """
        tests = []
        
        # Teste 1: Verificar informações da conta de negócios
        try:
            url = f"{self.BASE_URL}/{self.account.business_account_id}"
            params = {'fields': 'id,name,timezone_offset_min'}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                tests.append({
                    'test': 'Business Account Info',
                    'status': 'PASS',
                    'data': data
                })
            else:
                tests.append({
                    'test': 'Business Account Info',
                    'status': 'FAIL',
                    'error': f"HTTP {response.status_code}: {response.text}"
                })
        except Exception as e:
            tests.append({
                'test': 'Business Account Info',
                'status': 'ERROR',
                'error': str(e)
            })
        
        # Teste 2: Listar templates existentes
        try:
            url = f"{self.BASE_URL}/{self.account.business_account_id}/message_templates"
            params = {'limit': 1}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                tests.append({
                    'test': 'List Templates Permission',
                    'status': 'PASS',
                    'data': data
                })
            else:
                tests.append({
                    'test': 'List Templates Permission',
                    'status': 'FAIL',
                    'error': f"HTTP {response.status_code}: {response.text}"
                })
        except Exception as e:
            tests.append({
                'test': 'List Templates Permission',
                'status': 'ERROR',
                'error': str(e)
            })
        
        # Teste 3: Token info
        try:
            url = f"{self.BASE_URL}/me"
            params = {'fields': 'id,name'}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                tests.append({
                    'test': 'Token Info',
                    'status': 'PASS',
                    'data': data
                })
            else:
                tests.append({
                    'test': 'Token Info',
                    'status': 'FAIL',
                    'error': f"HTTP {response.status_code}: {response.text}"
                })
        except Exception as e:
            tests.append({
                'test': 'Token Info',
                'status': 'ERROR',
                'error': str(e)
            })
        
        # Verifica se todos os testes passaram
        all_passed = all(test['status'] == 'PASS' for test in tests)
        
        return {
            'success': all_passed,
            'tests': tests,
            'message': 'Todos os testes passaram' if all_passed else 'Alguns testes falharam'
        }
    
    def get_recent_messages(self, limit: int = 20) -> Dict[str, Any]:
        """
        Busca mensagens recentes via API do WhatsApp (Cloud API)
        Nota: A API do WhatsApp Business Cloud não tem endpoint direto para listar mensagens
        Este método deve ser implementado com base no seu webhook/armazenamento local
        """
        # Por limitações da API, mensagens devem ser recebidas via webhook
        # Esta função serve como placeholder para implementação futura
        logger.warning("get_recent_messages: API do WhatsApp não fornece endpoint para buscar mensagens históricas")
        return {
            'success': False,
            'error': 'API do WhatsApp Business Cloud API não suporta busca de mensagens históricas',
            'messages': [],
            'note': 'Mensagens devem ser recebidas via webhook e armazenadas localmente'
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
        from asgiref.sync import sync_to_async
        
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
        
        # Busca ou cria conversa ANTES de criar a mensagem
        conversation = await self._get_or_create_conversation(contact, timestamp)
        
        # Salva mensagem no banco
        message = await sync_to_async(WhatsAppMessage.objects.create)(
            wamid=wamid,
            account=self.account,
            contact=contact,
            conversation=conversation,  # Vincula à conversa
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
        
        # Se mensagem tem mídia, faz download assíncrono
        if message.is_media and message.media_id:
            # Faz download da mídia em background (não bloqueia o webhook)
            import asyncio
            asyncio.create_task(self._download_message_media(message))
        
        # Atualiza última atividade da conversa
        await sync_to_async(lambda: setattr(conversation, 'last_activity', timestamp) or conversation.save(update_fields=['last_activity']))()
        
        # Notifica nova mensagem via WebSocket
        await self._notify_new_message(message, conversation)
        
        # Se é uma nova conversa, notifica também
        if conversation.messages.count() == 1:  # Primeira mensagem da conversa
            await self._notify_new_conversation(conversation)
        
        logger.info(f"Mensagem inbound processada: {wamid} - Conversa: {conversation.id}")
    
    async def _get_or_create_conversation(self, contact, timestamp):
        """
        Busca ou cria uma conversa para o contato
        """
        from asgiref.sync import sync_to_async
        from core.models import WhatsAppConversation
        
        # Verifica se já existe conversa ativa para este contato
        existing_conversation = await sync_to_async(
            WhatsAppConversation.objects.filter(
                account=self.account,
                contact=contact,
                status__in=['pending', 'assigned', 'in_progress']  # Conversas ativas
            ).first
        )()
        
        if existing_conversation:
            logger.info(f"Usando conversa existente {existing_conversation.id} para contato {contact.display_name}")
            return existing_conversation
        
        # Cria nova conversa em status 'pending' (aguardando atendimento)
        new_conversation = await sync_to_async(WhatsAppConversation.objects.create)(
            account=self.account,
            contact=contact,
            status='pending',  # Nova conversa sempre em pendente
            first_message_at=timestamp,
            priority='medium'  # Prioridade padrão
        )
        
        logger.info(f"Nova conversa criada {new_conversation.id} para contato {contact.display_name}")
        return new_conversation
    
    async def _process_status_update(self, status_data: Dict):
        """
        Processa atualização de status de mensagem
        """
        from asgiref.sync import sync_to_async
        
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
        from asgiref.sync import sync_to_async
        
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
    
    async def _notify_new_message(self, message, conversation):
        """
        Notifica nova mensagem via WebSocket
        """
        from channels.layers import get_channel_layer
        
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
            
            # Notifica área comercial
            await channel_layer.group_send(
                'whatsapp_comercial',
                {
                    'type': 'message_received',
                    'message': message_data,
                    'conversation_id': conversation.id
                }
            )
    
    async def _notify_new_conversation(self, conversation):
        """
        Notifica nova conversa aguardando atendimento via WebSocket
        """
        from channels.layers import get_channel_layer
        from asgiref.sync import sync_to_async
        
        channel_layer = get_channel_layer()
        if channel_layer:
            # Serializa conversa
            conversation_data = {
                'id': conversation.id,
                'contact_name': conversation.contact.display_name,
                'contact_phone': conversation.contact.display_phone,
                'account_name': conversation.account.name,
                'status': conversation.status,
                'priority': conversation.priority,
                'first_message_at': conversation.first_message_at.isoformat(),
                'last_activity': conversation.last_activity.isoformat(),
                'messages_count': await sync_to_async(conversation.messages.count)(),
                'unread_count': await sync_to_async(conversation.unread_messages_count)
            }
            
            # Notifica área comercial sobre nova conversa aguardando
            await channel_layer.group_send(
                'whatsapp_comercial',
                {
                    'type': 'conversation_new',
                    'conversation': conversation_data
                }
            )
            
            # Chat functionality removed - keeping only account-level notifications
    
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