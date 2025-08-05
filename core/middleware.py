# -*- coding: utf-8 -*-
import re
from django.conf import settings
from django.contrib.auth.middleware import LoginRequiredMiddleware as DjangoLoginRequiredMiddleware
from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware(DjangoLoginRequiredMiddleware):
    """
    Middleware customizado que permite exceções para URLs específicas
    como webhooks e APIs públicas que não precisam de autenticação.
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Verifica se existe configuração de URLs isentas
        if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
            path = request.path_info
            
            # Testa cada padrão de URL isenta
            for exempt_url in settings.LOGIN_EXEMPT_URLS:
                if re.match(exempt_url, path):
                    return None
        
        # Se não estiver isenta, aplica a lógica padrão
        return super().process_view(request, view_func, view_args, view_kwargs)