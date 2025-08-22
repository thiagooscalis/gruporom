# -*- coding: utf-8 -*-
from functools import wraps
from django.contrib.auth.decorators import login_required, user_passes_test
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
            'comercial': 'Comercial',
            'operacional': 'Operacional',
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


def administracao_required(view_func):
    """
    Decorator que requer que o usuário pertença ao grupo 'Administração'
    """
    def check_admin(user):
        return user.groups.filter(name='Administração').exists()
    
    @wraps(view_func)
    @login_required
    @user_passes_test(check_admin)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    
    return wrapper


def comercial_required(view_func):
    """
    Decorator que requer que o usuário pertença ao grupo 'Comercial'
    """
    def check_comercial(user):
        return user.groups.filter(name='Comercial').exists()
    
    @wraps(view_func)
    @login_required
    @user_passes_test(check_comercial)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    
    return wrapper


def operacional_required(view_func):
    """
    Decorator que requer que o usuário pertença ao grupo 'Operacional'
    """
    def check_operacional(user):
        return user.groups.filter(name='Operacional').exists()
    
    @wraps(view_func)
    @login_required
    @user_passes_test(check_operacional)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    
    return wrapper


def promotor_required(view_func):
    """
    Decorator que requer que o usuário pertença ao grupo 'Promotor'
    """
    def check_promotor(user):
        return user.groups.filter(name='Promotor').exists()
    
    @wraps(view_func)
    @login_required
    @user_passes_test(check_promotor)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    
    return wrapper


def multi_area_required(*areas):
    """
    Decorator que permite acesso a usuários de múltiplas áreas
    
    Uso: @multi_area_required('Administração', 'Comercial')
    """
    def decorator(view_func):
        def check_multi_area(user):
            return user.groups.filter(name__in=areas).exists()
        
        @wraps(view_func)
        @login_required
        @user_passes_test(check_multi_area)
        def wrapper(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator