# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Prefetch
from core.decorators import comercial_required
from core.models import Caravana, Bloqueio


@comercial_required
def nova_venda(request):
    """
    Página principal de Nova Venda com opções de produtos/serviços
    """
    context = {
        'title': 'Nova Venda',
    }
    
    return render(request, 'comercial/pre_vendas/nova_venda.html', context)


@comercial_required
def caravanas_ativas(request):
    """
    View para listar caravanas ativas na área de pré-vendas
    """
    # Filtro de busca por nome
    search = request.GET.get('search', '')
    
    # Query otimizada com apenas dados necessários
    caravanas_qs = Caravana.objects.filter(ativo=True).select_related(
        'empresa', 'promotor'
    ).prefetch_related(
        'lideres',
        # Prefetch apenas o primeiro bloqueio ordenado por data de saída
        Prefetch(
            'bloqueio_set',
            queryset=Bloqueio.objects.order_by('saida')[:1],
            to_attr='primeiro_bloqueio'
        )
    ).order_by('nome')  # Ordenação consistente para paginação
    
    if search:
        caravanas_qs = caravanas_qs.filter(nome__icontains=search)
    
    # Paginação eficiente
    paginator = Paginator(caravanas_qs, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Evitar query extra para count - usar info do paginator
    total_caravanas = paginator.count
    
    context = {
        'title': 'Caravanas Ativas',
        'caravanas': page_obj,
        'search': search,
        'total_caravanas': total_caravanas,
    }
    
    # Resposta HTMX para carregamento dinâmico
    if request.headers.get('HX-Request'):
        if request.GET.get('load_more'):
            return render(request, 'comercial/pre_vendas/caravanas_partial_linhas.html', context)
        return render(request, 'comercial/pre_vendas/caravanas_partial_lista.html', context)
    
    return render(request, 'comercial/pre_vendas/caravanas_lista.html', context)


@comercial_required
def caravana_venda(request, pk):
    """
    Página para venda de uma caravana específica
    """
    caravana = get_object_or_404(
        Caravana.objects.select_related(
            'empresa', 'promotor', 'responsavel'
        ).prefetch_related(
            'lideres',
            'bloqueio_set__passageiro_set__pessoa',
            'bloqueio_set__voo_set',
            'bloqueio_set__diaroteiro_set'
        ),
        pk=pk,
        ativo=True
    )
    
    # Buscar bloqueios ordenados por data de saída
    bloqueios = caravana.bloqueio_set.filter(ativo=True).order_by('saida')
    
    # Calcular estatísticas de passageiros
    total_passageiros = sum(bloqueio.passageiro_set.count() for bloqueio in bloqueios)
    vagas_disponiveis = caravana.quantidade - total_passageiros
    
    context = {
        'title': f'Venda - {caravana.nome}',
        'caravana': caravana,
        'bloqueios': bloqueios,
        'total_passageiros': total_passageiros,
        'vagas_disponiveis': vagas_disponiveis,
    }
    
    return render(request, 'comercial/pre_vendas/caravana_venda.html', context)


@comercial_required
def bloqueio_modal(request, pk):
    """
    Modal com detalhes completos do bloqueio para seleção de venda
    """
    bloqueio = get_object_or_404(
        Bloqueio.objects.select_related(
            'caravana'
        ).prefetch_related(
            'paises',
            'inclusos',
            'hoteis',
            'voo_set__cia_aerea',
            'voo_set__aeroporto_embarque',
            'voo_set__aeroporto_desembarque',
            'diaroteiro_set',
            'extra_set',
            'passageiro_set__pessoa'
        ),
        pk=pk,
        ativo=True
    )
    
    # Calcular vagas disponíveis para este bloqueio
    passageiros_cadastrados = bloqueio.passageiro_set.count()
    vagas_disponiveis = bloqueio.caravana.quantidade - passageiros_cadastrados
    
    context = {
        'bloqueio': bloqueio,
        'passageiros_cadastrados': passageiros_cadastrados,
        'vagas_disponiveis': vagas_disponiveis,
        'range_vagas': range(1, min(vagas_disponiveis + 1, 61)),  # Limite máximo de 60 passageiros por vez
    }
    
    return render(request, 'comercial/pre_vendas/bloqueio_modal.html', context)


@comercial_required
def bloqueio_venda(request, pk):
    """
    Cria uma nova venda para o bloqueio e redireciona para a página de venda
    """
    from django.shortcuts import redirect
    from core.models import VendaBloqueio
    
    bloqueio = get_object_or_404(
        Bloqueio.objects.select_related('caravana'),
        pk=pk,
        ativo=True
    )
    
    # Verificar vagas disponíveis
    passageiros_cadastrados = bloqueio.passageiro_set.count()
    vagas_disponiveis = bloqueio.caravana.quantidade - passageiros_cadastrados
    
    if vagas_disponiveis <= 0:
        context = {
            'title': 'Sem Vagas Disponíveis',
            'bloqueio': bloqueio,
            'error': 'Este bloqueio não possui vagas disponíveis no momento.'
        }
        return render(request, 'comercial/pre_vendas/bloqueio_sem_vagas.html', context)
    
    # Criar nova venda em rascunho
    venda = VendaBloqueio.objects.create(
        bloqueio=bloqueio,
        vendedor=request.user,
        valor_unitario=bloqueio.valor_convertido,
        status='rascunho'
    )
    
    # Redirecionar para a página de venda
    return redirect('comercial:venda_detalhes', pk=venda.id)


@comercial_required
def venda_detalhes(request, pk):
    """
    Página multi-step para processar a venda
    """
    from core.models import VendaBloqueio, Pessoa
    
    venda = get_object_or_404(
        VendaBloqueio.objects.select_related(
            'bloqueio__caravana',
            'cliente',
            'vendedor'
        ).prefetch_related(
            'bloqueio__paises',
            'bloqueio__inclusos',
            'bloqueio__hoteis',
            'bloqueio__extra_set',
            'bloqueio__passageiro_set__pessoa'
        ),
        pk=pk
    )
    
    # Calcular vagas disponíveis
    passageiros_cadastrados = venda.bloqueio.passageiro_set.count()
    vagas_disponiveis = venda.bloqueio.caravana.quantidade - passageiros_cadastrados
    
    # Verificação de cliente existente via HTMX
    if request.method == 'POST' and request.headers.get('HX-Request'):
        documento = request.POST.get('documento', '').strip()
        
        # Remover caracteres especiais do documento
        documento_limpo = ''.join(filter(str.isdigit, documento))
        
        if documento_limpo:
            try:
                pessoa = Pessoa.objects.get(doc=documento_limpo)
                # Cliente existe - retornar dados preenchidos
                context = {
                    'pessoa': pessoa,
                    'venda': venda,
                    'bloqueio': venda.bloqueio,
                    'documento': documento_limpo,
                    'cliente_existente': True
                }
                return render(request, 'comercial/pre_vendas/venda_form_cliente.html', context)
            except Pessoa.DoesNotExist:
                # Cliente novo - retornar formulário em branco
                context = {
                    'venda': venda,
                    'bloqueio': venda.bloqueio,
                    'documento': documento_limpo,
                    'cliente_existente': False
                }
                return render(request, 'comercial/pre_vendas/venda_form_cliente.html', context)
    
    context = {
        'title': f'Venda - {venda.bloqueio.caravana.nome}',
        'venda': venda,
        'bloqueio': venda.bloqueio,
        'passageiros_cadastrados': passageiros_cadastrados,
        'vagas_disponiveis': vagas_disponiveis,
    }
    
    return render(request, 'comercial/pre_vendas/venda_inicio.html', context)