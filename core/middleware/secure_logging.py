# -*- coding: utf-8 -*-
"""
Middleware para logging seguro de requisições
"""

import json
import logging
from django.conf import settings
from core.utils.secure_logger import get_secure_logger

logger = get_secure_logger(__name__)


class SecureLoggingMiddleware:
    """
    Middleware que registra requisições de forma segura
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.is_production = not settings.DEBUG
    
    def __call__(self, request):
        # Log da requisição de entrada (apenas informações não sensíveis)
        self._log_request(request)
        
        response = self.get_response(request)
        
        # Log da resposta (apenas status e timing)
        self._log_response(request, response)
        
        return response
    
    def _log_request(self, request):
        """Log seguro de requisições"""
        if not self._should_log_request(request):
            return
        
        safe_data = {
            'method': request.method,
            'path': request.path,
            'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anônimo',
            'ip': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', 'Desconhecido')[:100],  # Limita tamanho
        }
        
        # Em desenvolvimento, adiciona mais detalhes
        if not self.is_production:
            safe_data.update({
                'query_params': dict(request.GET) if request.GET else {},
                'content_type': request.content_type,
            })
        
        logger.info(f"Requisição recebida", extra=safe_data)
    
    def _log_response(self, request, response):
        """Log seguro de respostas"""
        if not self._should_log_request(request):
            return
        
        safe_data = {
            'method': request.method,
            'path': request.path,
            'status': response.status_code,
            'content_type': response.get('Content-Type', 'Desconhecido'),
        }
        
        # Log apenas se houver erro ou em desenvolvimento
        if response.status_code >= 400 or not self.is_production:
            logger.info(f"Resposta enviada", extra=safe_data)
    
    def _should_log_request(self, request):
        """Determina se a requisição deve ser logada"""
        # Não loga requisições de arquivos estáticos
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return False
        
        # Não loga health checks
        if request.path in ['/health/', '/ping/', '/status/']:
            return False
        
        # Em produção, loga apenas rotas importantes
        if self.is_production:
            important_paths = [
                '/login/',
                '/logout/',
                '/webhook/',
                '/api/',
                '/comercial/',
                '/administracao/',
            ]
            return any(request.path.startswith(path) for path in important_paths)
        
        return True
    
    def _get_client_ip(self, request):
        """Obtém IP do cliente de forma segura"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'Desconhecido')
        
        # Em produção, mascara os últimos octetos do IP
        if self.is_production and '.' in ip:
            ip_parts = ip.split('.')
            if len(ip_parts) == 4:
                ip = f"{ip_parts[0]}.{ip_parts[1]}.***.**"
        
        return ip
    
    def process_exception(self, request, exception):
        """Log seguro de exceções"""
        safe_data = {
            'method': request.method,
            'path': request.path,
            'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anônimo',
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
        }
        
        logger.error(f"Exceção não tratada na requisição", extra=safe_data)
        
        # Em produção, não propaga detalhes da exceção
        if self.is_production:
            return None
        
        return None


class WebhookSecurityMiddleware:
    """
    Middleware específico para webhooks que remove dados sensíveis dos logs
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.is_production = not settings.DEBUG
    
    def __call__(self, request):
        # Para webhooks, registra apenas informações básicas
        if request.path.startswith('/webhook/'):
            self._log_webhook_request(request)
        
        response = self.get_response(request)
        return response
    
    def _log_webhook_request(self, request):
        """Log específico para webhooks"""
        webhook_data = {
            'path': request.path,
            'method': request.method,
            'content_length': request.META.get('CONTENT_LENGTH', 0),
            'content_type': request.content_type,
            'user_agent': request.META.get('HTTP_USER_AGENT', 'Desconhecido')[:50],
        }
        
        # Em desenvolvimento, adiciona mais detalhes (mas ainda seguro)
        if not self.is_production:
            try:
                if request.content_type == 'application/json' and request.body:
                    payload = json.loads(request.body)
                    # Log apenas estrutura, não conteúdo
                    webhook_data['payload_structure'] = {
                        'keys': list(payload.keys()) if isinstance(payload, dict) else 'not_dict',
                        'size_bytes': len(request.body)
                    }
            except (json.JSONDecodeError, UnicodeDecodeError):
                webhook_data['payload_structure'] = 'invalid_json'
        
        logger.info("Webhook recebido", extra=webhook_data)