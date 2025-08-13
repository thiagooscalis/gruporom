# -*- coding: utf-8 -*-
"""
Context processors para disponibilizar dados globalmente nos templates
"""
from datetime import date
from django.utils.text import slugify
from core.models import Cambio
import logging

logger = logging.getLogger(__name__)


def cambio_do_dia(request):
    """
    Context processor que disponibiliza o câmbio do dia em todos os templates

    Uso nos templates:
    {{ cambio_hoje.valor }} - Valor da cotação
    {{ cambio_hoje.data }} - Data da cotação
    {{ cambio_hoje }} - String formatada
    """
    try:
        cambio = Cambio.obter_cambio(date.today())
        return {
            "cambio_hoje": cambio,
            "dolar_hoje": cambio.valor if cambio else None,
        }
    except Exception as e:
        logger.error(f"Erro ao obter câmbio no context processor: {e}")
        return {
            "cambio_hoje": None,
            "dolar_hoje": None,
        }


def dados_globais(request):
    """
    Context processor para dados globais do sistema
    Pode ser expandido com outros dados que precisem estar disponíveis globalmente
    """
    # Detecta a área atual baseada nos grupos do usuário e URL
    area = None
    tipos_empresa_usuario = []
    
    if request.user.is_authenticated:
        try:
            for group in request.user.groups.all():
                group_slug = slugify(group.name)
                if f"/{group_slug}/" in request.path:
                    area = group_slug
                    break
            
            # Obtém os tipos de empresa do usuário
            if hasattr(request.user, 'empresas'):
                tipos_set = set(
                    request.user.empresas.filter(empresa_gruporom=True)
                    .values_list('tipo_empresa', flat=True)
                )
                tipos_empresa_usuario = list(tipos_set)
        except Exception:
            # Se há erro de transação, retorna valores padrão
            pass

    return {
        "sistema_nome": "Grupo ROM",
        "sistema_versao": "1.0.0",
        "data_atual": date.today(),
        "area": area,
        "tipos_empresa_usuario": tipos_empresa_usuario,
    }
