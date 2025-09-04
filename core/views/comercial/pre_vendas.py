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
from core.models.pais import Pais
from core.models.passageiro import Passageiro
from core.services.venda_service import VendaService
from core.forms.pessoa import PessoaForm


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
        
        # Criar a venda em pré-venda (sem cliente definido inicialmente)
        venda = VendaBloqueio.objects.create(
            bloqueio=bloqueio,
            cliente=None,  # Cliente deve ser definido após criação da pré-venda
            vendedor=request.user,
            status='pre-venda',
            numero_passageiros=int(quantidade) if quantidade else 1,  # Usar a quantidade informada
            observacoes=f'Venda iniciada a partir da caravana: {caravana.nome}'
        )
        
        messages.success(request, f'Pré-venda {venda.codigo} criada com sucesso! Agora defina o comprador, adicione passageiros e registre pagamentos.')
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
    View para adicionar passageiro à venda usando o PessoaForm
    """
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    
    try:
        # Verificar se ainda pode adicionar passageiros
        if venda.passageiros.count() >= venda.numero_passageiros:
            messages.error(request, f'Limite de passageiros atingido. Máximo permitido: {venda.numero_passageiros}')
            return render(request, 'comercial/pre_vendas/partials/passageiros_lista_principal.html', {'venda': venda})
        
        documento = request.POST.get('doc', '').strip()
        tipo = request.POST.get('tipo', '')
        
        if not documento:
            messages.error(request, 'Documento é obrigatório.')
            return render(request, 'comercial/pre_vendas/partials/passageiros_lista_principal.html', {'venda': venda})
        
        # Limpar documento
        doc_limpo = ''.join(filter(str.isalnum, documento))
        
        # Verificar se já existe
        pessoa = Pessoa.objects.filter(
            Q(doc=doc_limpo) | 
            Q(passaporte_numero=doc_limpo)
        ).first()
        
        if pessoa:
            # Atualizar pessoa existente com dados do form
            form = PessoaForm(request.POST, instance=pessoa)
        else:
            # Criar nova pessoa
            form = PessoaForm(request.POST)
            
            # Definir tipo de documento baseado no formato
            form_data = form.data.copy()
            if len(doc_limpo) == 14:
                form_data['doc'] = doc_limpo
                form_data['tipo_doc'] = 'CNPJ'
            elif len(doc_limpo) == 11 and doc_limpo.isdigit():
                form_data['doc'] = doc_limpo
                form_data['tipo_doc'] = 'CPF'
            else:
                # Se não for CPF nem CNPJ, considerar como passaporte
                form_data['passaporte_numero'] = doc_limpo
                form_data['doc'] = doc_limpo
                form_data['tipo_doc'] = 'Passaporte'
            form.data = form_data
        
        if form.is_valid():
            pessoa = form.save()
            
            # Usar o service para adicionar passageiro
            service = VendaService()
            passageiro = service.adicionar_passageiro_venda(
                venda_id=venda.id,
                pessoa_id=pessoa.id
            )
            
            # Definir tipo (sempre normal neste contexto)
            if tipo:
                passageiro.tipo = tipo
                passageiro.save()
            
            messages.success(request, f'Passageiro {pessoa.nome} adicionado com sucesso!')
        else:
            # Retornar erros do formulário
            errors = []
            for field, errs in form.errors.items():
                for err in errs:
                    errors.append(f"{field}: {err}")
            messages.error(request, f'Erro ao cadastrar passageiro: {"; ".join(errors)}')
        
    except Exception as e:
        messages.error(request, f'Erro ao adicionar passageiro: {str(e)}')
    
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
    
    return render(request, 'comercial/pre_vendas/partials/passageiros_lista_principal.html', context)


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
    
    return render(request, 'comercial/pre_vendas/partials/passageiros_lista_principal.html', context)

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


# Views para gerenciar extras
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def gerenciar_extras_modal(request, venda_id):
    """
    View para exibir modal de gerenciamento de extras
    """
    from core.models.extra import Extra
    
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    
    # Buscar extras disponíveis
    extras_disponiveis = Extra.objects.filter(ativo=True)
    
    context = {
        'venda': venda,
        'extras_disponiveis': extras_disponiveis,
    }
    
    return render(request, 'comercial/pre_vendas/modals/gerenciar_extras.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def adicionar_extra(request, venda_id):
    """
    View para adicionar extra à venda
    """
    from core.models.extra import Extra, ExtraVenda
    
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    extra_id = request.POST.get('extra_id')
    quantidade = int(request.POST.get('quantidade', 1))
    valor_unitario = float(request.POST.get('valor_unitario', 0).replace('R$', '').replace('.', '').replace(',', '.'))
    observacoes = request.POST.get('observacoes', '')
    
    try:
        extra = get_object_or_404(Extra, pk=extra_id)
        
        # Criar o extra da venda
        extra_venda = ExtraVenda.objects.create(
            venda=venda,
            extra=extra,
            quantidade=quantidade,
            valor_unitario=valor_unitario or extra.valor,
            observacoes=observacoes
        )
        
        # Recalcular totais
        service = VendaService()
        service._recalcular_totais_venda(venda)
        
        messages.success(request, f'Extra {extra.nome} adicionado com sucesso!')
    except Exception as e:
        messages.error(request, f'Erro ao adicionar extra: {str(e)}')
    
    venda.refresh_from_db()
    
    context = {
        'venda': venda,
    }
    
    return render(request, 'comercial/pre_vendas/partials/lista_extras.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_http_methods(["DELETE"])
def remover_extra(request, venda_id, extra_id):
    """
    View para remover extra da venda
    """
    from core.models.extra import ExtraVenda
    
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    extra_venda = get_object_or_404(ExtraVenda, pk=extra_id, venda=venda)
    
    try:
        nome_extra = extra_venda.extra.nome
        extra_venda.delete()
        
        # Recalcular totais
        service = VendaService()
        service._recalcular_totais_venda(venda)
        
        messages.success(request, f'Extra {nome_extra} removido com sucesso!')
    except Exception as e:
        messages.error(request, f'Erro ao remover extra: {str(e)}')
    
    venda.refresh_from_db()
    
    context = {
        'venda': venda,
    }
    
    return render(request, 'comercial/pre_vendas/partials/lista_extras.html', context)


# Views para gerenciar pagamentos
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def gerenciar_pagamentos_modal(request, venda_id):
    """
    View para exibir modal de gerenciamento de pagamentos
    """
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    
    context = {
        'venda': venda,
    }
    
    return render(request, 'comercial/pre_vendas/modals/gerenciar_pagamentos.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def adicionar_pagamento(request, venda_id):
    """
    View para adicionar pagamento à venda
    """
    from datetime import datetime
    
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    
    try:
        valor = float(request.POST.get('valor', 0).replace('R$', '').replace('.', '').replace(',', '.'))
        forma_pagamento = request.POST.get('forma_pagamento')
        data_pagamento = request.POST.get('data_pagamento')
        status = request.POST.get('status', 'confirmado')
        referencia = request.POST.get('referencia', '')
        observacoes = request.POST.get('observacoes', '')
        
        # Converter data
        if data_pagamento:
            data_pagamento = datetime.strptime(data_pagamento, '%Y-%m-%dT%H:%M')
        else:
            data_pagamento = None
        
        # Usar o service para registrar o pagamento
        service = VendaService()
        pagamento = service.registrar_pagamento(
            venda_id=venda.id,
            dados_pagamento={
                'valor': valor,
                'forma_pagamento': forma_pagamento,
                'data_pagamento': data_pagamento,
                'status': status,
                'referencia': referencia,
                'observacoes': observacoes,
            }
        )
        
        messages.success(request, f'Pagamento de R$ {valor:.2f} registrado com sucesso!')
        
        if venda.esta_quitada:
            messages.info(request, 'Venda totalmente quitada!')
            
    except Exception as e:
        messages.error(request, f'Erro ao registrar pagamento: {str(e)}')
    
    venda.refresh_from_db()
    
    context = {
        'venda': venda,
    }
    
    return render(request, 'comercial/pre_vendas/partials/lista_pagamentos.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_http_methods(["DELETE"])
def cancelar_pagamento(request, pagamento_id):
    """
    View para cancelar pagamento
    """
    from core.models.pagamento import Pagamento
    
    pagamento = get_object_or_404(Pagamento, pk=pagamento_id)
    venda = pagamento.venda
    
    try:
        pagamento.status = 'cancelado'
        pagamento.save()
        
        # Recalcular totais
        service = VendaService()
        service._recalcular_totais_venda(venda)
        
        messages.success(request, 'Pagamento cancelado com sucesso!')
    except Exception as e:
        messages.error(request, f'Erro ao cancelar pagamento: {str(e)}')
    
    venda.refresh_from_db()
    
    context = {
        'venda': venda,
    }
    
    return render(request, 'comercial/pre_vendas/partials/lista_pagamentos.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def confirmar_pagamento(request, pagamento_id):
    """
    View para confirmar pagamento pendente
    """
    from core.models.pagamento import Pagamento
    
    pagamento = get_object_or_404(Pagamento, pk=pagamento_id)
    venda = pagamento.venda
    
    try:
        pagamento.status = 'confirmado'
        pagamento.save()
        
        # Recalcular totais
        service = VendaService()
        service._recalcular_totais_venda(venda)
        
        messages.success(request, 'Pagamento confirmado com sucesso!')
    except Exception as e:
        messages.error(request, f'Erro ao confirmar pagamento: {str(e)}')
    
    venda.refresh_from_db()
    
    context = {
        'venda': venda,
    }
    
    return render(request, 'comercial/pre_vendas/partials/lista_pagamentos.html', context)


# Views para gerenciar cliente/comprador
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def selecionar_cliente_modal(request, venda_id):
    """
    View para exibir modal de seleção de cliente
    """
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    
    context = {
        'venda': venda,
    }
    
    return render(request, 'comercial/pre_vendas/modals/selecionar_cliente.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def definir_cliente(request, venda_id):
    """
    View para definir/alterar cliente da venda
    """
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    cliente_id = request.POST.get('cliente_id')
    
    if not cliente_id:
        return HttpResponse(
            '<div class="alert alert-danger">Selecione um cliente.</div>'
        )
    
    try:
        cliente = get_object_or_404(Pessoa, pk=cliente_id)
        venda.cliente = cliente
        venda.save()
        
        messages.success(request, f'Cliente {cliente.nome} definido com sucesso!')
        
        # Trigger evento para recarregar página
        return HttpResponse("""
            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                Cliente definido com sucesso!
            </div>
            <script>
                document.body.dispatchEvent(new Event('cliente-definido'));
            </script>
        """)
    except Exception as e:
        return HttpResponse(
            f'<div class="alert alert-danger">Erro ao definir cliente: {str(e)}</div>'
        )


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def buscar_clientes_autocomplete(request):
    """
    View para autocomplete de clientes
    """
    query = request.POST.get('busca_cliente', '')
    
    if len(query) < 2:
        return HttpResponse('')
    
    clientes = Pessoa.objects.filter(
        Q(nome__icontains=query) |
        Q(cpf__icontains=query) |
        Q(email__icontains=query)
    )[:10]
    
    html = '<div class="list-group position-absolute w-100 shadow" style="z-index: 1000; max-height: 300px; overflow-y: auto;">'
    for cliente in clientes:
        html += f'''
        <button type="button" class="list-group-item list-group-item-action"
                onclick="selecionarCliente({cliente.id}, '{cliente.nome}', '{cliente.cpf or ""}', '{cliente.email or ""}')">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>{cliente.nome}</strong>
                    <br>
                    <small class="text-muted">
                        {f"CPF: {cliente.cpf}" if cliente.cpf else ""}
                        {f" | {cliente.email}" if cliente.email else ""}
                    </small>
                </div>
                <i class="fas fa-chevron-right text-muted"></i>
            </div>
        </button>
        '''
    html += '</div>'
    
    return HttpResponse(html)


# Views auxiliares HTMX
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def buscar_pessoas_autocomplete(request):
    """
    View para autocomplete de pessoas
    """
    query = request.POST.get('busca_pessoa', '')
    
    if len(query) < 2:
        return HttpResponse('')
    
    pessoas = Pessoa.objects.filter(
        Q(nome__icontains=query) |
        Q(cpf__icontains=query) |
        Q(passaporte__icontains=query)
    )[:10]
    
    html = '<div class="list-group position-absolute w-100 shadow" style="z-index: 1000; max-height: 300px; overflow-y: auto;">'
    for pessoa in pessoas:
        doc = pessoa.cpf or pessoa.passaporte or 'Sem documento'
        html += f'''
        <button type="button" class="list-group-item list-group-item-action"
                onclick="selecionarPessoa({pessoa.id}, '{pessoa.nome}')">
            <div class="d-flex justify-content-between">
                <strong>{pessoa.nome}</strong>
                <small class="text-muted">{doc}</small>
            </div>
        </button>
        '''
    html += '</div>'
    
    return HttpResponse(html)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def listar_passageiros(request, venda_id):
    """
    View para listar passageiros da venda via HTMX
    """
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    
    context = {
        'venda': venda,
    }
    
    return render(request, 'comercial/pre_vendas/partials/passageiros_lista_principal.html', context)


@login_required  
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def buscar_por_documento(request):
    """
    View para buscar pessoa por documento via HTMX
    """
    documento = request.POST.get('doc', '').strip()
    
    if not documento:
        return HttpResponse('')
    
    # Limpar documento removendo formatação
    doc_limpo = ''.join(filter(str.isalnum, documento))
    
    try:
        # Buscar pessoa por documento ou passaporte
        pessoa = Pessoa.objects.filter(
            Q(doc=doc_limpo) | 
            Q(passaporte_numero=doc_limpo)
        ).first()
        
        # Obter lista de países para o formulário
        paises = Pais.objects.all().order_by('nome')
        
        if pessoa:
            # Se encontrou, criar form com instance
            form = PessoaForm(instance=pessoa)
            context = {
                'form': form,
                'pessoa': pessoa,
                'pessoa_encontrada': True,
                'paises': paises
            }
        else:
            # Se não encontrou, criar form vazio
            form = PessoaForm()
            context = {
                'form': form,
                'pessoa_encontrada': False,
                'paises': paises
            }
            
        return render(request, 'comercial/pre_vendas/partials/dados_pessoa.html', context)
        
    except Exception as e:
        return HttpResponse('')


@login_required  
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def buscar_por_documento_passageiro(request):
    """
    View para buscar pessoa por documento via HTMX (para passageiros)
    """
    documento = request.POST.get('doc', '').strip()
    
    if not documento:
        return HttpResponse('')
    
    # Limpar documento removendo formatação
    doc_limpo = ''.join(filter(str.isalnum, documento))
    
    try:
        # Buscar pessoa por documento ou passaporte
        pessoa = Pessoa.objects.filter(
            Q(doc=doc_limpo) | 
            Q(passaporte_numero=doc_limpo)
        ).first()
        
        # Obter lista de países para o formulário
        paises = Pais.objects.all().order_by('nome')
        
        if pessoa:
            # Se encontrou, criar form com instance
            form = PessoaForm(instance=pessoa)
            context = {
                'form': form,
                'pessoa': pessoa,
                'pessoa_encontrada': True,
                'paises': paises,
                'is_passageiro': True  # Flag para identificar que é para passageiro
            }
        else:
            # Se não encontrou, criar form vazio
            form = PessoaForm()
            context = {
                'form': form,
                'pessoa_encontrada': False,
                'paises': paises,
                'is_passageiro': True  # Flag para identificar que é para passageiro
            }
            
        return render(request, 'comercial/pre_vendas/partials/dados_pessoa_passageiro.html', context)
        
    except Exception as e:
        return HttpResponse('')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def upload_passaporte_modal(request, pessoa_id):
    """
    View para exibir modal de upload de passaporte
    """
    pessoa = get_object_or_404(Pessoa, pk=pessoa_id)
    
    context = {
        'pessoa': pessoa,
    }
    
    return render(request, 'comercial/pre_vendas/modals/upload_passaporte.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def upload_passaporte(request, pessoa_id):
    """
    View para fazer upload do passaporte
    """
    pessoa = get_object_or_404(Pessoa, pk=pessoa_id)
    
    try:
        if 'passaporte_copia' in request.FILES:
            pessoa.passaporte_copia = request.FILES['passaporte_copia']
        
        # Atualizar outros campos de passaporte se fornecidos
        passaporte_numero = request.POST.get('passaporte_numero', '').strip()
        passaporte_nome = request.POST.get('passaporte_nome', '').strip()
        passaporte_validade = request.POST.get('passaporte_validade', '').strip()
        
        if passaporte_numero:
            pessoa.passaporte_numero = passaporte_numero
        if passaporte_nome:
            pessoa.passaporte_nome = passaporte_nome
        if passaporte_validade:
            from datetime import datetime
            try:
                pessoa.passaporte_validade = datetime.strptime(passaporte_validade, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        pessoa.save()
        
        return HttpResponse(
            '<div class="alert alert-success">Passaporte carregado com sucesso!</div>'
            '<script>setTimeout(() => { '
            'document.getElementById("htmxModal").querySelector(".btn-close").click(); '
            'location.reload(); '
            '}, 1000);</script>'
        )
        
    except Exception as e:
        return HttpResponse(
            f'<div class="alert alert-danger">Erro ao carregar passaporte: {str(e)}</div>'
        )


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def cadastrar_comprador(request, venda_id):
    """
    View para cadastrar/atualizar comprador via HTMX
    """
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    
    try:
        documento = request.POST.get('doc', '').strip()
        
        if not documento:
            return HttpResponse(
                '<div class="alert alert-danger">Documento é obrigatório.</div>'
            )
        
        # Limpar documento
        doc_limpo = ''.join(filter(str.isalnum, documento))
        
        # Verificar se já existe
        pessoa = Pessoa.objects.filter(
            Q(doc=doc_limpo) | 
            Q(passaporte_numero=doc_limpo)
        ).first()
        
        if pessoa:
            # Atualizar pessoa existente
            form = PessoaForm(request.POST, instance=pessoa)
        else:
            # Criar nova pessoa
            form = PessoaForm(request.POST)
            
            # Definir tipo de documento baseado no formato
            if len(doc_limpo) == 14:
                form.data = form.data.copy()
                form.data['doc'] = doc_limpo
                form.data['tipo_doc'] = 'CNPJ'
            elif len(doc_limpo) == 11 and doc_limpo.isdigit():
                form.data = form.data.copy()
                form.data['doc'] = doc_limpo
                form.data['tipo_doc'] = 'CPF'
            else:
                # Se não for CPF nem CNPJ, considerar como passaporte
                form.data = form.data.copy()
                form.data['passaporte_numero'] = doc_limpo
                form.data['doc'] = doc_limpo
                form.data['tipo_doc'] = 'Passaporte'
        
        if form.is_valid():
            pessoa = form.save()
            
            # Associar pessoa à venda
            venda.cliente = pessoa
            venda.save()
            
            # Disparar evento JavaScript para recarregar página
            response = HttpResponse(
                '<div class="alert alert-success">Comprador cadastrado com sucesso!</div>'
                '<script>document.body.dispatchEvent(new CustomEvent("comprador-cadastrado"));</script>'
            )
            
            return response
        else:
            # Retornar erros do formulário
            errors = '<br>'.join([f"{field}: {', '.join(errs)}" for field, errs in form.errors.items()])
            return HttpResponse(
                f'<div class="alert alert-danger">Erro ao cadastrar comprador:<br>{errors}</div>'
            )
        
    except Exception as e:
        return HttpResponse(
            f'<div class="alert alert-danger">Erro ao cadastrar comprador: {str(e)}</div>'
        )


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_http_methods(["DELETE"])
def remover_venda(request, venda_id):
    """
    View para remover venda (apenas pré-vendas podem ser removidas)
    """
    from django.http import HttpResponse
    
    venda = get_object_or_404(VendaBloqueio, pk=venda_id)
    
    # Verificar se pode remover (apenas pré-vendas)
    if venda.status != 'pre-venda':
        return HttpResponse(
            '<div class="alert alert-danger">Apenas pré-vendas podem ser removidas.</div>',
            status=403
        )
    
    try:
        # Remover passageiros da venda (desvincula, não deleta)
        venda.passageiros.update(venda=None)
        
        # Deletar pagamentos
        venda.pagamentos.all().delete()
        
        # Deletar extras
        venda.extravenda_set.all().delete()
        
        # Deletar a venda
        venda.delete()
        
        # Retornar resposta vazia para o HTMX remover a linha
        return HttpResponse('')
        
    except Exception as e:
        return HttpResponse(
            f'<div class="alert alert-danger">Erro ao remover venda: {str(e)}</div>',
            status=500
        )

