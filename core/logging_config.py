# -*- coding: utf-8 -*-
"""
Configuração de logging segura para produção
Remove automaticamente informações sensíveis dos logs
"""

import logging
import re
from typing import Any


class SecureFormatter(logging.Formatter):
    """
    Formatter que remove informações sensíveis dos logs
    """
    
    # Padrões para remover dos logs
    SENSITIVE_PATTERNS = [
        # Tokens e chaves
        r'token["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_\-]+["\']?',
        r'key["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_\-]+["\']?',
        r'password["\']?\s*[:=]\s*["\']?[^"\'\s]+["\']?',
        r'secret["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_\-]+["\']?',
        
        # Headers de autorização
        r'Authorization["\']?\s*[:=]\s*["\']?Bearer\s+[a-zA-Z0-9_\-\.]+["\']?',
        r'X-\w+-Token["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_\-]+["\']?',
        
        # Números de telefone completos
        r'\+\d{10,15}',
        
        # CPFs e CNPJs
        r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}',
        r'\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}',
        
        # URLs com parâmetros sensíveis
        r'https?://[^\s]*(?:token|key|password|secret)=[^&\s]*',
        
        # JSON com chaves sensíveis
        r'"(?:token|key|password|secret|authorization)":\s*"[^"]*"',
    ]
    
    def format(self, record: logging.LogRecord) -> str:
        # Formata a mensagem normalmente
        formatted = super().format(record)
        
        # Remove informações sensíveis apenas em produção
        if not getattr(record, 'is_development', False):
            formatted = self._sanitize_message(formatted)
        
        return formatted
    
    def _sanitize_message(self, message: str) -> str:
        """Remove informações sensíveis da mensagem"""
        for pattern in self.SENSITIVE_PATTERNS:
            message = re.sub(pattern, '[DADOS_SENSÍVEIS_REMOVIDOS]', message, flags=re.IGNORECASE)
        
        return message


class ProductionFilter(logging.Filter):
    """
    Filtro que bloqueia logs muito verbosos em produção
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        # Em produção, bloqueia logs de debug
        if record.levelno < logging.INFO:
            return False
        
        # Bloqueia logs específicos que podem vazar informação
        sensitive_messages = [
            'Headers:',
            'Payload:',
            'Body bruto:',
            'Resposta completa:',
            'traceback',
            'Traceback',
        ]
        
        message = record.getMessage().lower()
        for sensitive in sensitive_messages:
            if sensitive.lower() in message:
                return False
        
        return True


def setup_secure_logging():
    """
    Configura logging seguro para produção
    """
    import os
    from django.conf import settings
    
    # Aplica filtros apenas em produção
    is_production = not settings.DEBUG
    
    if is_production:
        # Obtém todos os loggers do projeto
        project_loggers = [
            'core.services.whatsapp_api',
            'core.views.administracao.whatsapp',
            'core.views.comercial.whatsapp',
            'core.models.cambio',
            'core.consumers',
            'django.request',
            'django.security',
        ]
        
        for logger_name in project_loggers:
            logger = logging.getLogger(logger_name)
            
            # Adiciona filtro de produção
            logger.addFilter(ProductionFilter())
            
            # Substitui formatters por versão segura
            for handler in logger.handlers:
                if handler.formatter:
                    handler.setFormatter(SecureFormatter(handler.formatter._fmt))


# Configuração específica para diferentes ambientes
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'secure': {
            '()': SecureFormatter,
            'format': '{asctime} {levelname} {name}: {message}',
            'style': '{',
        },
        'development': {
            'format': '{asctime} {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'filters': {
        'production_filter': {
            '()': ProductionFilter,
        },
    },
    'handlers': {
        'console_secure': {
            'class': 'logging.StreamHandler',
            'formatter': 'secure',
            'filters': ['production_filter'],
        },
        'console_dev': {
            'class': 'logging.StreamHandler',
            'formatter': 'development',
        },
    },
    'root': {
        'handlers': ['console_secure'],
        'level': 'INFO',
    },
    'loggers': {
        'core': {
            'handlers': ['console_secure'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console_secure'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console_secure'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}