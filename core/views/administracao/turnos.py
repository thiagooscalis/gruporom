# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from core.models import Turno
from core.forms import TurnoForm


@login_required
def lista(request):
    """Lista todos os turnos com busca e paginação"""
    search = request.GET.get('search', '')
    
    turnos = Turno.objects.all()
    
    if search:
        turnos = turnos.filter(
            Q(nome__icontains=search)
        )
    
    paginator = Paginator(turnos, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'area': 'administracao'
    }
    
    return render(request, 'administracao/turnos/lista.html', context)


@login_required
def novo_modal(request):
    """Retorna o modal para criar novo turno via HTMX"""
    form = TurnoForm()
    return render(request, 'administracao/turnos/modal_form.html', {
        'form': form,
        'title': 'Novo Turno',
        'action_url': 'administracao:turnos_criar'
    })


@login_required
def criar(request):
    """Cria novo turno via HTMX"""
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            try:
                turno = form.save()
                messages.success(request, f'Turno "{turno.nome}" criado com sucesso!')
                
                # Retorna script para fechar modal e recarregar página
                return HttpResponse("""
                    <script>
                        const modal = bootstrap.Modal.getInstance(document.getElementById('modalTurno'));
                        if (modal) modal.hide();
                        window.location.reload();
                    </script>
                """)
            except Exception as e:
                form.add_error(None, f'Erro ao salvar: {str(e)}')
        
        # Retorna formulário com erros
        return render(request, 'administracao/turnos/modal_form.html', {
            'form': form,
            'title': 'Novo Turno',
            'action_url': 'administracao:turnos_criar'
        })
    
    return redirect('administracao:turnos_lista')


@login_required
def editar_modal(request, pk):
    """Retorna o modal para editar turno via HTMX"""
    turno = get_object_or_404(Turno, pk=pk)
    form = TurnoForm(instance=turno)
    return render(request, 'administracao/turnos/modal_form.html', {
        'form': form,
        'title': f'Editar Turno - {turno.nome}',
        'action_url': 'administracao:turnos_atualizar',
        'turno_id': turno.id
    })


@login_required
def atualizar(request, pk):
    """Atualiza turno via HTMX"""
    turno = get_object_or_404(Turno, pk=pk)
    
    if request.method == 'POST':
        form = TurnoForm(request.POST, instance=turno)
        if form.is_valid():
            try:
                turno = form.save()
                messages.success(request, f'Turno "{turno.nome}" atualizado com sucesso!')
                
                # Retorna script para fechar modal e recarregar página
                return HttpResponse("""
                    <script>
                        const modal = bootstrap.Modal.getInstance(document.getElementById('modalTurno'));
                        if (modal) modal.hide();
                        window.location.reload();
                    </script>
                """)
            except Exception as e:
                form.add_error(None, f'Erro ao salvar: {str(e)}')
        
        # Retorna formulário com erros
        return render(request, 'administracao/turnos/modal_form.html', {
            'form': form,
            'title': f'Editar Turno - {turno.nome}',
            'action_url': 'administracao:turnos_atualizar',
            'turno_id': turno.id
        })
    
    return redirect('administracao:turnos_lista')


@login_required
def excluir_modal(request, pk):
    """Retorna o modal para confirmar exclusão do turno via HTMX"""
    turno = get_object_or_404(Turno, pk=pk)
    return render(request, 'administracao/turnos/modal_excluir.html', {
        'turno': turno,
        'title': f'Excluir Turno - {turno.nome}',
        'action_url': 'administracao:turnos_excluir',
    })


@login_required
def excluir(request, pk):
    """Exclui turno via HTMX"""
    turno = get_object_or_404(Turno, pk=pk)
    
    if request.method == 'POST':
        try:
            nome_turno = turno.nome
            turno.delete()
            messages.success(request, f'Turno "{nome_turno}" excluído com sucesso!')
            
            # Retorna script para fechar modal e recarregar página
            return HttpResponse("""
                <script>
                    const modal = bootstrap.Modal.getInstance(document.getElementById('modalTurno'));
                    if (modal) modal.hide();
                    window.location.reload();
                </script>
            """)
        except Exception as e:
            messages.error(request, f'Erro ao excluir turno: {str(e)}')
            return render(request, 'administracao/turnos/modal_excluir.html', {
                'turno': turno,
                'title': f'Excluir Turno - {turno.nome}',
                'action_url': 'administracao:turnos_excluir',
                'error': str(e)
            })
    
    return redirect('administracao:turnos_lista')