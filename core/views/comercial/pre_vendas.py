# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.http import require_POST
from core.models.caravana import Caravana
from core.models.venda import VendaBloqueio
from core.models.bloqueio import Bloqueio


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


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def iniciar_venda_caravana(request, caravana_id):
    """
    View para criar uma venda a partir de uma caravana
    """
    caravana = get_object_or_404(Caravana, pk=caravana_id)
    
    # Obter dados do formulário
    bloqueio_id = request.POST.get('bloqueio_id')
    quantidade = request.POST.get('quantidade')
    
    try:
        # Buscar o bloqueio selecionado
        bloqueio = None
        if bloqueio_id:
            bloqueio = get_object_or_404(Bloqueio, pk=bloqueio_id)
        
        # Criar a venda em rascunho
        venda = VendaBloqueio.objects.create(
            bloqueio=bloqueio,
            cliente=caravana.responsavel,  # Usar o responsável da caravana como cliente inicial
            vendedor=request.user,
            status='rascunho',
            numero_passageiros=int(quantidade) if quantidade else 0,
            observacoes=f'Venda iniciada a partir da caravana: {caravana.nome}'
        )
        
        messages.success(request, f'Venda {venda.codigo} criada com sucesso!')
        return redirect('comercial:pre_venda_detalhe', venda_id=venda.id)
        
    except Exception as e:
        messages.error(request, f'Erro ao criar venda: {str(e)}')
        return redirect('comercial:caravana_detalhes', caravana_id=caravana.id)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def pre_venda_detalhe(request, venda_id):
    """
    View para exibir e editar detalhes de uma pré-venda
    """
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    
    # Verificar se o usuário pode editar esta venda
    if venda.vendedor != request.user and not request.user.is_superuser:
        messages.warning(request, 'Você não tem permissão para editar esta venda.')
        return redirect('comercial:pre_vendas_lista')
    
    context = {
        'title': f'Pré-venda {venda.codigo}',
        'venda': venda,
    }
    
    return render(request, 'comercial/pre_vendas/venda_detalhe.html', context)