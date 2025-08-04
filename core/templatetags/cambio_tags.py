# -*- coding: utf-8 -*-
"""
Template tags relacionados a câmbio
"""
from django import template
from datetime import date, timedelta
from core.models import Cambio
import logging

register = template.Library()
logger = logging.getLogger(__name__)


@register.simple_tag
def cambio_data(data_consulta=None):
    """
    Template tag para obter câmbio de uma data específica
    
    Uso: {% cambio_data "2025-08-01" %}
    Uso: {% cambio_data %} (data atual)
    """
    try:
        if data_consulta:
            if isinstance(data_consulta, str):
                # Converte string para date
                ano, mes, dia = data_consulta.split('-')
                data_consulta = date(int(ano), int(mes), int(dia))
        else:
            data_consulta = date.today()
        
        cambio = Cambio.obter_cambio(data_consulta)
        return cambio
    except Exception as e:
        logger.error(f"Erro no template tag cambio_data: {e}")
        return None


@register.simple_tag
def valor_dolar(data_consulta=None):
    """
    Template tag para obter apenas o valor do dólar
    
    Uso: {% valor_dolar %}
    Uso: {% valor_dolar "2025-08-01" %}
    """
    cambio = cambio_data(data_consulta)
    return cambio.valor if cambio else None


@register.simple_tag
def dolar_formatado(data_consulta=None):
    """
    Template tag para obter dólar formatado como string
    
    Uso: {% dolar_formatado %} -> "R$ 5,5055"
    """
    valor = valor_dolar(data_consulta)
    if valor:
        return f"R$ {valor:,.4f}".replace('.', ',').replace(',', '.', 1)
    return "N/A"


@register.filter
def converter_dolar(valor_real, data_consulta=None):
    """
    Filter para converter valor em reais para dólar
    
    Uso: {{ 100|converter_dolar }} -> valor em dólar
    Uso: {{ valor|converter_dolar:"2025-08-01" }}
    """
    try:
        if not valor_real:
            return 0
        
        cotacao = valor_dolar(data_consulta)
        if cotacao:
            return float(valor_real) / float(cotacao)
        return 0
    except (ValueError, TypeError):
        return 0


@register.filter  
def converter_real(valor_dolar_input, data_consulta=None):
    """
    Filter para converter valor em dólar para reais
    
    Uso: {{ 100|converter_real }} -> valor em reais
    """
    try:
        if not valor_dolar_input:
            return 0
        
        cotacao = valor_dolar(data_consulta)
        if cotacao:
            return float(valor_dolar_input) * float(cotacao)
        return 0
    except (ValueError, TypeError):
        return 0


@register.inclusion_tag('components/cambio_widget.html')
def widget_cambio(mostrar_data=True, mostrar_variacao=False):
    """
    Inclusion tag para widget de câmbio
    
    Uso: {% widget_cambio %}
    Uso: {% widget_cambio mostrar_data=False %}
    """
    try:
        cambio_hoje = Cambio.obter_cambio(date.today())
        cambio_ontem = None
        variacao = None
        
        if mostrar_variacao and cambio_hoje:
            ontem = date.today() - timedelta(days=1)
            cambio_ontem = Cambio.obter_cambio(ontem)
            
            if cambio_ontem:
                variacao = cambio_hoje.valor - cambio_ontem.valor
        
        return {
            'cambio_hoje': cambio_hoje,
            'cambio_ontem': cambio_ontem,
            'variacao': variacao,
            'mostrar_data': mostrar_data,
            'mostrar_variacao': mostrar_variacao,
        }
    except Exception as e:
        logger.error(f"Erro no widget_cambio: {e}")
        return {
            'cambio_hoje': None,
            'erro': True,
        }