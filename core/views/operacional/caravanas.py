# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
from core.models import Caravana
from core.forms.caravana import CaravanaForm
from core.choices import TIPO_CARAVANA_CHOICES


def is_operacional(user):
    """Verifica se o usuário pertence ao grupo Operacional"""
    return user.groups.filter(name='Operacional').exists()


@login_required
@user_passes_test(is_operacional)
def caravanas_lista(request):
    """Listagem de caravanas com busca e paginação"""
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    tipo_filter = request.GET.get('tipo', '')
    
    caravanas = Caravana.objects.select_related(
        'empresa', 'promotor'
    ).prefetch_related('lideres')
    
    # Filtro de busca
    if search:
        caravanas = caravanas.filter(
            Q(nome__icontains=search) |
            Q(promotor__nome__icontains=search) |
            Q(empresa__nome__icontains=search) |
            Q(lideres__nome__icontains=search)
        ).distinct()
    
    # Filtro de tipo
    if tipo_filter:
        caravanas = caravanas.filter(tipo=tipo_filter)
    
    # Anotações úteis
    caravanas = caravanas.annotate(
        total_lideres=Count('lideres')
    )
    
    # Ordenação
    caravanas = caravanas.order_by('-data_contrato', 'nome')
    
    # Paginação
    paginator = Paginator(caravanas, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Calcula quantos registros restam
    restantes = page_obj.paginator.count - page_obj.end_index() if page_obj.has_next() else 0
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'tipo_filter': tipo_filter,
        'restantes': restantes,
        'tipos_caravana': TIPO_CARAVANA_CHOICES,
    }
    
    # Resposta HTMX
    if request.headers.get('HX-Request'):
        if request.GET.get('load_more'):
            return render(request, 'operacional/caravanas/partial_linhas.html', context)
        else:
            return render(request, 'operacional/caravanas/partial_lista.html', context)
    
    return render(request, 'operacional/caravanas/lista.html', context)


@login_required
@user_passes_test(is_operacional)
def caravana_criar_modal(request):
    """Cria nova caravana via modal"""
    if request.method == 'POST':
        form = CaravanaForm(request.POST, user=request.user)
        if form.is_valid():
            caravana = form.save()
            messages.success(request, f'Caravana "{caravana.nome}" criada com sucesso!')
            
            # Retorna resposta HTMX
            response = HttpResponse()
            response['HX-Trigger'] = 'caravanaCreated'
            response['HX-Refresh'] = 'true'
            return response
    else:
        form = CaravanaForm(user=request.user)
    
    return render(request, 'operacional/caravanas/modal_form.html', {
        'form': form,
        'titulo': 'Nova Caravana',
        'action_url': request.path,
        'modal_id': 'caravanaModal',
    })


@login_required
@user_passes_test(is_operacional)
def caravana_editar_modal(request, pk):
    """Edita caravana existente via modal"""
    caravana = get_object_or_404(Caravana, pk=pk)
    
    if request.method == 'POST':
        form = CaravanaForm(request.POST, instance=caravana, user=request.user)
        if form.is_valid():
            caravana = form.save()
            messages.success(request, f'Caravana "{caravana.nome}" atualizada com sucesso!')
            
            # Retorna resposta HTMX
            response = HttpResponse()
            response['HX-Trigger'] = 'caravanaUpdated'
            response['HX-Refresh'] = 'true'
            return response
    else:
        form = CaravanaForm(instance=caravana, user=request.user)
    
    return render(request, 'operacional/caravanas/modal_form.html', {
        'form': form,
        'caravana': caravana,
        'titulo': f'Editar Caravana: {caravana.nome}',
        'action_url': request.path,
    })


@login_required
@user_passes_test(is_operacional)
def caravana_excluir_modal(request, pk):
    """Exclui caravana via modal de confirmação"""
    caravana = get_object_or_404(Caravana, pk=pk)
    
    if request.method == 'POST':
        nome = caravana.nome
        try:
            caravana.delete()
            messages.success(request, f'Caravana "{nome}" excluída com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir caravana: {str(e)}')
        
        # Retorna resposta HTMX
        response = HttpResponse()
        response['HX-Trigger'] = 'caravanaDeleted'
        response['HX-Refresh'] = 'true'
        return response
    
    return render(request, 'operacional/caravanas/modal_excluir.html', {
        'caravana': caravana,
    })


@login_required
@user_passes_test(is_operacional)
def caravana_detalhes(request, pk):
    """Visualiza detalhes completos da caravana"""
    caravana = get_object_or_404(
        Caravana.objects.select_related(
            'empresa', 'promotor'
        ).prefetch_related(
            'lideres'
        ),
        pk=pk
    )
    
    # Estatísticas da caravana
    stats = {
        'total_lideres': caravana.lideres.count(),
        'total_quantidade': caravana.quantidade,
        'total_free': caravana.free_economica + caravana.free_executiva,
    }
    
    return render(request, 'operacional/caravanas/detalhes.html', {
        'caravana': caravana,
        'stats': stats,
    })