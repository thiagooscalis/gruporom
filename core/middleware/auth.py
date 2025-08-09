# -*- coding: utf-8 -*-
import re
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Middleware customizado que requer autenticação para todas as views,
    mas permite exceções para URLs específicas como webhooks e APIs públicas.
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # URLs que não precisam de autenticação
        exempt_urls = [
            r'^/admin/',
            r'^/login/',
            r'^/logout/',
            r'^/webhook/',
        ]
        
        # Verifica se existe configuração de URLs isentas adicional
        if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
            exempt_urls.extend(settings.LOGIN_EXEMPT_URLS)
        
        path = request.path_info
        
        # Testa cada padrão de URL isenta
        for exempt_url in exempt_urls:
            if re.match(exempt_url, path):
                return None
        
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            # Importação lazy para evitar problemas de inicialização
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        
        return None