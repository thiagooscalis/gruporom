# -*- coding: utf-8 -*-
from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied


def group_area_required(view_func):
    """
    Decorator que verifica se o usuário pertence ao grupo correspondente
    à primeira parte da URL (área).
    
    Por exemplo, se a URL é /administracao/usuarios/, verifica se o usuário
    tem o grupo "Administração" (antes do slugify).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Extrai a área da URL
        path_parts = request.path.strip('/').split('/')
        if not path_parts:
            raise PermissionDenied("Área não encontrada na URL")
        
        area_slug = path_parts[0]
        
        # Mapeia slugs para nomes de grupos
        # Adicione mais mapeamentos conforme necessário
        slug_to_group = {
            'administracao': 'Administração',
            # Adicione outros mapeamentos aqui
        }
        
        group_name = slug_to_group.get(area_slug)
        if not group_name:
            raise PermissionDenied(f"Área '{area_slug}' não reconhecida")
        
        # Verifica se o usuário tem o grupo
        if not request.user.groups.filter(name=group_name).exists():
            raise PermissionDenied(f"Usuário não tem acesso à área '{group_name}'")
        
        # Adiciona a área ao request para uso nas views
        request.area = area_slug
        
        return view_func(request, *args, **kwargs)
    
    return wrapper