# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def pre_vendas_lista(request):
    """
    View para listagem de pré-vendas
    """
    # Por enquanto retornando lista vazia
    pre_vendas = []
    search = request.GET.get('search', '')
    
    # Paginação
    paginator = Paginator(pre_vendas, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Pré-vendas',
        'page_obj': page_obj,
        'search': search,
        'restantes': page_obj.paginator.count - page_obj.end_index() if page_obj.has_next() else 0,
    }
    
    # HTMX Detection
    if request.headers.get('HX-Request'):
        if request.GET.get('load_more'):
            return render(request, 'comercial/pre_vendas/vendas_partial_linhas.html', context)
        else:
            return render(request, 'comercial/pre_vendas/vendas_partial_lista.html', context)
    
    return render(request, 'comercial/pre_vendas/vendas_lista.html', context)