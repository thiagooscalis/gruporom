# -*- coding: utf-8 -*-
"""
Context processors para disponibilizar dados globalmente nos templates
"""
from datetime import date
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
            'cambio_hoje': cambio,
            'dolar_hoje': cambio.valor if cambio else None,
        }
    except Exception as e:
        logger.error(f"Erro ao obter câmbio no context processor: {e}")
        return {
            'cambio_hoje': None,
            'dolar_hoje': None,
        }


def dados_globais(request):
    """
    Context processor para dados globais do sistema
    Pode ser expandido com outros dados que precisem estar disponíveis globalmente
    """
    return {
        'sistema_nome': 'Grupo ROM',
        'sistema_versao': '1.0.0',
        'data_atual': date.today(),
    }