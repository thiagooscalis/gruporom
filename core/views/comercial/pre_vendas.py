# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from core.models.caravana import Caravana
from core.models.venda import VendaBloqueio
from core.models.bloqueio import Bloqueio
from core.models.pessoa import Pessoa
from core.models.passageiro import Passageiro
from core.services.venda_service import VendaService


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def pre_vendas_lista(request):
    """
    View para listagem de pré-vendas
    """
    # Buscar filtros
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Usar o service para listar vendas
    service = VendaService()
    filtros = {}
    
    if search:
        filtros['busca'] = search
    
    if status_filter:
        filtros['status'] = status_filter
    else:
        # Por padrão, mostrar apenas pré-vendas
        filtros['status'] = 'pre-venda'
    
    # Obter vendas do usuário ou todas se for admin
    vendas_queryset = service.listar_vendas_usuario(
        usuario=request.user,
        filtros=filtros
    )
    
    # Paginação
    paginator = Paginator(vendas_queryset, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Opções de status para filtro
    status_choices = [
        ('', 'Todas as vendas'),
        ('pre-venda', 'Pré-venda'),
        ('confirmada', 'Confirmada'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]
    
    context = {
        'title': 'Pré-vendas',
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'status_choices': status_choices,
        'restantes': page_obj.paginator.count - page_obj.end_index() if page_obj.has_next() else 0,
        'total_vendas': paginator.count,
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
        
        # Criar a venda em pré-venda
        venda = VendaBloqueio.objects.create(
            bloqueio=bloqueio,
            cliente=caravana.responsavel,  # Usar o responsável da caravana como cliente inicial
            vendedor=request.user,
            status='pre-venda',
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


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def gerenciar_passageiros_modal(request, venda_id):
    """
    View para exibir modal de gerenciamento de passageiros
    """
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    
    # Calcular passageiros disponíveis
    passageiros_vendidos = Passageiro.objects.filter(
        bloqueio=venda.bloqueio,
        venda__isnull=False,
        venda__status__in=['confirmada', 'concluida']
    ).exclude(venda=venda).count()
    
    passageiros_disponiveis = venda.bloqueio.caravana.quantidade - passageiros_vendidos - venda.numero_passageiros
    
    context = {
        'venda': venda,
        'passageiros_disponiveis': passageiros_disponiveis,
    }
    
    return render(request, 'comercial/pre_vendas/modals/gerenciar_passageiros.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def buscar_pessoa_passageiro(request):
    """
    View para buscar pessoas via HTMX
    """
    query = request.GET.get('pessoa_search', '')
    results = []
    
    if query and len(query) >= 2:
        pessoas = Pessoa.objects.filter(
            Q(nome__icontains=query) | 
            Q(cpf__icontains=query) | 
            Q(passaporte__icontains=query)
        )[:10]
        
        results = list(pessoas.values('id', 'nome', 'cpf', 'passaporte', 'email'))
    
    context = {
        'results': results,
        'query': query,
    }
    
    return render(request, 'comercial/pre_vendas/partials/pessoa_search_results.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def selecionar_pessoa_passageiro(request):
    """
    View para selecionar uma pessoa no autocomplete
    """
    pessoa_id = request.POST.get('pessoa_id')
    pessoa_nome = request.POST.get('pessoa_nome')
    
    context = {
        'pessoa_id': pessoa_id,
        'pessoa_nome': pessoa_nome,
    }
    
    return render(request, 'comercial/pre_vendas/partials/pessoa_selected.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def limpar_pessoa_passageiro(request):
    """
    View para limpar a seleção de pessoa
    """
    return HttpResponse('')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def adicionar_passageiro(request, venda_id):
    """
    View para adicionar passageiro à venda
    """
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    pessoa_id = request.POST.get('pessoa_id')
    tipo = request.POST.get('tipo', '')
    
    if not pessoa_id:
        messages.error(request, 'Selecione uma pessoa para adicionar como passageiro.')
    else:
        try:
            service = VendaService()
            passageiro = service.adicionar_passageiro_venda(
                venda_id=venda.id,
                pessoa_id=pessoa_id
            )
            
            # Se tipo especial foi selecionado, atualizar
            if tipo:
                passageiro.tipo = tipo
                passageiro.save()
            
            messages.success(request, f'Passageiro {passageiro.pessoa.nome} adicionado com sucesso!')
        except Exception as e:
            messages.error(request, str(e))
    
    # Recarregar venda com dados atualizados
    venda.refresh_from_db()
    
    # Calcular passageiros disponíveis
    passageiros_vendidos = Passageiro.objects.filter(
        bloqueio=venda.bloqueio,
        venda__isnull=False,
        venda__status__in=['confirmada', 'concluida']
    ).exclude(venda=venda).count()
    
    passageiros_disponiveis = venda.bloqueio.caravana.quantidade - passageiros_vendidos - venda.numero_passageiros
    
    context = {
        'venda': venda,
        'passageiros_disponiveis': passageiros_disponiveis,
    }
    
    return render(request, 'comercial/pre_vendas/partials/lista_passageiros.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_http_methods(["DELETE"])
def remover_passageiro(request, venda_id, passageiro_id):
    """
    View para remover passageiro da venda
    """
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    passageiro = get_object_or_404(Passageiro, pk=passageiro_id, venda=venda)
    
    try:
        nome_passageiro = passageiro.pessoa.nome
        passageiro.venda = None
        passageiro.save()
        
        # Recalcular totais da venda
        service = VendaService()
        service._recalcular_totais_venda(venda)
        
        messages.success(request, f'Passageiro {nome_passageiro} removido com sucesso!')
    except Exception as e:
        messages.error(request, f'Erro ao remover passageiro: {str(e)}')
    
    # Recarregar venda com dados atualizados
    venda.refresh_from_db()
    
    # Calcular passageiros disponíveis
    passageiros_vendidos = Passageiro.objects.filter(
        bloqueio=venda.bloqueio,
        venda__isnull=False,
        venda__status__in=['confirmada', 'concluida']
    ).exclude(venda=venda).count()
    
    passageiros_disponiveis = venda.bloqueio.caravana.quantidade - passageiros_vendidos - venda.numero_passageiros
    
    context = {
        'venda': venda,
        'passageiros_disponiveis': passageiros_disponiveis,
    }
    
    return render(request, 'comercial/pre_vendas/partials/lista_passageiros.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name="Comercial").exists())
def registrar_pagamento_modal(request, venda_id):
    """
    View para exibir modal de registro de pagamento
    """
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    
    # Verificar se pode adicionar pagamento
    if not venda.pode_adicionar_pagamento:
        messages.warning(request, "Esta venda não permite novos pagamentos.")
        return HttpResponse("")
    
    context = {
        "venda": venda,
    }
    
    return render(request, "comercial/pre_vendas/modals/registrar_pagamento.html", context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name="Comercial").exists())
@require_POST
def registrar_pagamento(request, venda_id):
    """
    View para registrar um pagamento
    """
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    
    # Verificar permissão
    if venda.vendedor != request.user and not request.user.is_superuser:
        return render(request, "comercial/pre_vendas/partials/pagamento_feedback.html", {
            "error": "Você não tem permissão para registrar pagamentos nesta venda."
        })
    
    # Obter dados do formulário
    try:
        valor = float(request.POST.get("valor", 0))
        forma_pagamento = request.POST.get("forma_pagamento")
        referencia = request.POST.get("referencia", "")
        observacoes = request.POST.get("observacoes", "")
        
        if not forma_pagamento:
            raise ValueError("Forma de pagamento é obrigatória.")
        
        # Usar o service para registrar o pagamento
        service = VendaService()
        pagamento = service.registrar_pagamento(
            venda_id=venda.id,
            dados_pagamento={
                "valor": valor,
                "forma_pagamento": forma_pagamento,
                "referencia": referencia,
                "observacoes": observacoes,
            }
        )
        
        # Recarregar venda para pegar valores atualizados
        venda.refresh_from_db()
        
        # Mensagem de sucesso com informações adicionais
        if venda.valor_pendente == 0:
            messages.success(request, f"Pagamento de R$ {valor:.2f} registrado! Venda totalmente paga.")
        else:
            messages.success(request, f"Pagamento de R$ {valor:.2f} registrado! Pendente: {venda.valor_pendente_formatado}")
        
        return render(request, "comercial/pre_vendas/partials/pagamento_feedback.html", {
            "success": True,
            "messages": messages.get_messages(request)
        })
        
    except Exception as e:
        return render(request, "comercial/pre_vendas/partials/pagamento_feedback.html", {
            "error": str(e)
        })


@login_required
@user_passes_test(lambda u: u.groups.filter(name="Comercial").exists())
def confirmar_venda_modal(request, venda_id):
    """
    View para exibir modal de confirmação de venda
    """
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    
    if not venda.pode_confirmar:
        messages.warning(request, "Esta venda não pode ser confirmada.")
        return HttpResponse("")
    
    context = {
        "venda": venda,
    }
    
    return render(request, "comercial/pre_vendas/modals/confirmar_venda.html", context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name="Comercial").exists())
@require_POST
def confirmar_venda(request, venda_id):
    """
    View para confirmar uma venda
    """
    try:
        service = VendaService()
        venda = service.confirmar_venda(venda_id=venda_id, usuario=request.user)
        
        messages.success(request, f"Venda {venda.codigo} confirmada com sucesso!")
        
        # Retornar script para fechar modal e recarregar página
        return HttpResponse("""
            <script>
                bootstrap.Modal.getInstance(document.getElementById("htmxModal")).hide();
                setTimeout(() => location.reload(), 1500);
            </script>
            <div class="toast-container position-fixed bottom-0 end-0 p-3">
                <div class="toast show bg-success text-white">
                    <div class="toast-body">
                        <i class="fas fa-check-circle me-2"></i>
                        Venda confirmada com sucesso!
                    </div>
                </div>
            </div>
        """)
    except Exception as e:
        messages.error(request, str(e))
        return HttpResponse(f'<div class="alert alert-danger m-3">{str(e)}</div>')


@login_required
@user_passes_test(lambda u: u.groups.filter(name="Comercial").exists())
def cancelar_venda_modal(request, venda_id):
    """
    View para exibir modal de cancelamento de venda
    """
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    
    if not venda.pode_cancelar:
        messages.warning(request, "Esta venda não pode ser cancelada.")
        return HttpResponse("")
    
    context = {
        "venda": venda,
    }
    
    return render(request, "comercial/pre_vendas/modals/cancelar_venda.html", context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name="Comercial").exists())
@require_POST
def cancelar_venda(request, venda_id):
    """
    View para cancelar uma venda
    """
    motivo = request.POST.get("motivo", "").strip()
    
    if not motivo:
        return HttpResponse(
            '<div class="alert alert-danger m-3">O motivo do cancelamento é obrigatório.</div>'
        )
    
    try:
        service = VendaService()
        venda = service.cancelar_venda(
            venda_id=venda_id,
            motivo=motivo,
            usuario=request.user
        )
        
        messages.success(request, f"Venda {venda.codigo} cancelada com sucesso.")
        
        # Retornar script para fechar modal e recarregar página
        return HttpResponse("""
            <script>
                bootstrap.Modal.getInstance(document.getElementById("htmxModal")).hide();
                setTimeout(() => location.reload(), 1500);
            </script>
            <div class="toast-container position-fixed bottom-0 end-0 p-3">
                <div class="toast show bg-danger text-white">
                    <div class="toast-body">
                        <i class="fas fa-times-circle me-2"></i>
                        Venda cancelada com sucesso!
                    </div>
                </div>
            </div>
        """)
    except Exception as e:
        messages.error(request, str(e))
        return HttpResponse(f'<div class="alert alert-danger m-3">{str(e)}</div>')

