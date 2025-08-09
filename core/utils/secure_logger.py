# -*- coding: utf-8 -*-
"""
Logger seguro que automaticamente remove informações sensíveis
"""

import logging
import re
from typing import Any, Dict, Optional
from django.conf import settings


class SecureLogger:
    """
    Wrapper para logger que remove automaticamente informações sensíveis
    """
    
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
        self.is_production = not settings.DEBUG
    
    def _sanitize_data(self, data: Any) -> Any:
        """Remove dados sensíveis de qualquer estrutura de dados"""
        if not self.is_production:
            return data
        
        if isinstance(data, dict):
            return self._sanitize_dict(data)
        elif isinstance(data, str):
            return self._sanitize_string(data)
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        else:
            return data
    
    def _sanitize_dict(self, data: Dict) -> Dict:
        """Remove chaves sensíveis de dicionários"""
        sensitive_keys = {
            'password', 'token', 'key', 'secret', 'authorization',
            'access_token', 'refresh_token', 'api_key', 'private_key',
            'webhook_url', 'phone_number', 'cpf', 'cnpj', 'document',
            'headers', 'body', 'payload'  # Headers e payloads completos
        }
        
        sanitized = {}
        for key, value in data.items():
            key_lower = str(key).lower()
            
            # Remove chaves sensíveis completamente
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                sanitized[key] = '[REMOVIDO]'
            # Para outras chaves, sanitiza o valor recursivamente
            else:
                sanitized[key] = self._sanitize_data(value)
        
        return sanitized
    
    def _sanitize_string(self, text: str) -> str:
        """Remove padrões sensíveis de strings"""
        if not isinstance(text, str):
            return text
        
        # Padrões para mascarar
        patterns = [
            # Tokens e chaves (mantém apenas primeiros e últimos 4 caracteres)
            (r'token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{8,})["\']?', r'token=\1'),
            (r'Bearer\s+([a-zA-Z0-9_\-\.]{16,})', r'Bearer [TOKEN_MASCARADO]'),
            
            # Números de telefone (mantém DDI e primeiros 2 dígitos)
            (r'\+(\d{2})(\d{2})\d{5,}', r'+\1\2*****'),
            
            # CPF (mantém primeiros 3 e últimos 2 dígitos)
            (r'(\d{3})\.?\d{3}\.?\d{3}-?(\d{2})', r'\1.***.**-\2'),
            
            # CNPJ (mantém primeiros 2 e últimos 2 dígitos)
            (r'(\d{2})\.?\d{3}\.?\d{3}/?\d{4}-?(\d{2})', r'\1.***.***/****-\2'),
            
            # URLs (remove query parameters)
            (r'(https?://[^?\s]+)\?[^\s]*', r'\1?[PARAMS_REMOVIDOS]'),
        ]
        
        sanitized = text
        for pattern, replacement in patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def debug(self, message: str, extra: Optional[Dict] = None):
        """Log debug com sanitização"""
        if self.is_production:
            return  # Não loga debug em produção
        
        sanitized_message = self._sanitize_string(message)
        sanitized_extra = self._sanitize_data(extra) if extra else None
        
        self.logger.debug(sanitized_message, extra=sanitized_extra)
    
    def info(self, message: str, extra: Optional[Dict] = None):
        """Log info com sanitização"""
        sanitized_message = self._sanitize_string(message)
        sanitized_extra = self._sanitize_data(extra) if extra else None
        
        self.logger.info(sanitized_message, extra=sanitized_extra)
    
    def warning(self, message: str, extra: Optional[Dict] = None):
        """Log warning com sanitização"""
        sanitized_message = self._sanitize_string(message)
        sanitized_extra = self._sanitize_data(extra) if extra else None
        
        self.logger.warning(sanitized_message, extra=sanitized_extra)
    
    def error(self, message: str, extra: Optional[Dict] = None):
        """Log error com sanitização"""
        sanitized_message = self._sanitize_string(message)
        sanitized_extra = self._sanitize_data(extra) if extra else None
        
        self.logger.error(sanitized_message, extra=sanitized_extra)
    
    def critical(self, message: str, extra: Optional[Dict] = None):
        """Log critical com sanitização"""
        sanitized_message = self._sanitize_string(message)
        sanitized_extra = self._sanitize_data(extra) if extra else None
        
        self.logger.critical(sanitized_message, extra=sanitized_extra)
    
    def exception(self, message: str, extra: Optional[Dict] = None):
        """Log exception com sanitização (sem traceback em produção)"""
        sanitized_message = self._sanitize_string(message)
        
        if self.is_production:
            # Em produção, não inclui traceback
            self.logger.error(f"EXCEPTION: {sanitized_message}", extra=extra)
        else:
            # Em desenvolvimento, inclui traceback
            sanitized_extra = self._sanitize_data(extra) if extra else None
            self.logger.exception(sanitized_message, extra=sanitized_extra)


def get_secure_logger(name: str) -> SecureLogger:
    """
    Factory function para criar logger seguro
    """
    return SecureLogger(name)


# Exemplo de uso em outros arquivos:
# from core.utils.secure_logger import get_secure_logger
# logger = get_secure_logger(__name__)
# logger.info("Mensagem segura", extra={"data": sensitive_data})