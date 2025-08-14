import locale

from django import template
from django.utils.text import slugify
from django.utils import timezone
from datetime import datetime, timedelta


register = template.Library()


@register.filter
def moeda(val, format='R$'):
    if not val:
        val = 0
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    return locale.currency(val, grouping=True)


@register.filter
def fone(val):
    if len(val) == 10:
        return f'({val[0:2]}) {val[2:6]}-{val[6:]}'
    elif len(val) == 11:
        return f'({val[0:2]}) {val[2:7]}-{val[7:]}'
    return val


@register.filter
def doc(val):
    if not val:
        return val
    if len(val) == 11:
        return f'{val[0:3]}.{val[3:6]}.{val[6:9]}-{val[9:]}'
    if len(val) == 14:
        return f'{val[0:2]}.{val[2:5]}.{val[5:8]}/{val[8:12]}-{val[12:]}'
    return val


@register.filter
def area_icon(group_name):
    """Retorna o ícone FontAwesome para cada área/grupo"""
    icons = {
        'Administração': 'fa-cog',
        'Comercial': 'fa-chart-line',
        'Operacional': 'fa-tools',
        'Promotor': 'fa-bullhorn',
    }
    return icons.get(group_name, 'fa-th-large')


@register.filter  
def area_url(group_name):
    """Retorna a URL base para cada área/grupo"""
    area_slug = slugify(group_name)
    return f'{area_slug}:home'


@register.filter
def smart_datetime(timestamp):
    """
    Formata data/hora de forma inteligente:
    - Se for hoje: mostra apenas horário (HH:MM)
    - Se for ontem: mostra "Ontem HH:MM"
    - Se for este ano: mostra "DD/MM HH:MM"
    - Se for outro ano: mostra "DD/MM/AAAA HH:MM"
    """
    if not timestamp:
        return ""
    
    # Garante que estamos trabalhando com timezone-aware datetime
    if timezone.is_naive(timestamp):
        timestamp = timezone.make_aware(timestamp)
    
    now = timezone.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    timestamp_date = timestamp.date()
    
    # Formata o horário
    time_str = timestamp.strftime("%H:%M")
    
    # Decide o formato baseado na data
    if timestamp_date == today:
        # Hoje: apenas horário
        return time_str
    elif timestamp_date == yesterday:
        # Ontem
        return f"Ontem {time_str}"
    elif timestamp.year == now.year:
        # Este ano: dia/mês horário
        return timestamp.strftime("%d/%m %H:%M")
    else:
        # Outro ano: data completa
        return timestamp.strftime("%d/%m/%Y %H:%M")
