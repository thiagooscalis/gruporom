import locale

from django import template


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
    if len(val) == 11:
        return f'{val[0:3]}.{val[3:6]}.{val[6:9]}-{val[9:]}'
    if len(val) == 14:
        return f'{val[0:2]}.{val[2:5]}.{val[5:8]}-{val[8:]}'
    return doc
