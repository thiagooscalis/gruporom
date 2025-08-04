# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from core.models import Cargo
from core.forms import CargoForm


@login_required
def lista(request):
    """Lista todos os cargos com busca e paginação"""
    search = request.GET.get('search', '')
    
    cargos = Cargo.objects.select_related('empresa').all()
    
    if search:
        cargos = cargos.filter(
            Q(nome__icontains=search) |
            Q(empresa__nome__icontains=search)
        )
    
    paginator = Paginator(cargos, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'area': 'administracao'
    }
    
    return render(request, 'administracao/cargos/lista.html', context)


@login_required
def novo_modal(request):
    """Retorna o modal para criar novo cargo via HTMX"""
    form = CargoForm()
    return render(request, 'administracao/cargos/modal_form.html', {
        'form': form,
        'title': 'Novo Cargo',
        'action_url': 'administracao:cargos_criar'
    })


@login_required
def criar(request):
    """Cria novo cargo via HTMX"""
    if request.method == 'POST':
        form = CargoForm(request.POST)
        if form.is_valid():
            try:
                cargo = form.save()
                messages.success(request, f'Cargo "{cargo.nome}" criado com sucesso!')
                
                # Retorna script para fechar modal e recarregar página
                return HttpResponse("""
                    <script>
                        const modal = bootstrap.Modal.getInstance(document.getElementById('modalCargo'));
                        if (modal) modal.hide();
                        window.location.reload();
                    </script>
                """)
            except Exception as e:
                form.add_error(None, f'Erro ao salvar: {str(e)}')
        
        # Retorna formulário com erros
        return render(request, 'administracao/cargos/modal_form.html', {
            'form': form,
            'title': 'Novo Cargo',
            'action_url': 'administracao:cargos_criar'
        })
    
    return redirect('administracao:cargos_lista')


@login_required
def editar_modal(request, pk):
    """Retorna o modal para editar cargo via HTMX"""
    cargo = get_object_or_404(Cargo, pk=pk)
    form = CargoForm(instance=cargo)
    return render(request, 'administracao/cargos/modal_form.html', {
        'form': form,
        'title': f'Editar Cargo - {cargo.nome}',
        'action_url': 'administracao:cargos_atualizar',
        'cargo_id': cargo.id
    })


@login_required
def atualizar(request, pk):
    """Atualiza cargo via HTMX"""
    cargo = get_object_or_404(Cargo, pk=pk)
    
    if request.method == 'POST':
        form = CargoForm(request.POST, instance=cargo)
        if form.is_valid():
            try:
                cargo = form.save()
                messages.success(request, f'Cargo "{cargo.nome}" atualizado com sucesso!')
                
                # Retorna script para fechar modal e recarregar página
                return HttpResponse("""
                    <script>
                        const modal = bootstrap.Modal.getInstance(document.getElementById('modalCargo'));
                        if (modal) modal.hide();
                        window.location.reload();
                    </script>
                """)
            except Exception as e:
                form.add_error(None, f'Erro ao salvar: {str(e)}')
        
        # Retorna formulário com erros
        return render(request, 'administracao/cargos/modal_form.html', {
            'form': form,
            'title': f'Editar Cargo - {cargo.nome}',
            'action_url': 'administracao:cargos_atualizar',
            'cargo_id': cargo.id
        })
    
    return redirect('administracao:cargos_lista')


@login_required
def excluir_modal(request, pk):
    """Retorna o modal para confirmar exclusão do cargo via HTMX"""
    cargo = get_object_or_404(Cargo, pk=pk)
    return render(request, 'administracao/cargos/modal_excluir.html', {
        'cargo': cargo,
        'title': f'Excluir Cargo - {cargo.nome}',
        'action_url': 'administracao:cargos_excluir',
    })


@login_required
def excluir(request, pk):
    """Exclui cargo via HTMX"""
    cargo = get_object_or_404(Cargo, pk=pk)
    
    if request.method == 'POST':
        try:
            nome_cargo = cargo.nome
            cargo.delete()
            messages.success(request, f'Cargo "{nome_cargo}" excluído com sucesso!')
            
            # Retorna script para fechar modal e recarregar página
            return HttpResponse("""
                <script>
                    const modal = bootstrap.Modal.getInstance(document.getElementById('modalCargo'));
                    if (modal) modal.hide();
                    window.location.reload();
                </script>
            """)
        except Exception as e:
            messages.error(request, f'Erro ao excluir cargo: {str(e)}')
            return render(request, 'administracao/cargos/modal_excluir.html', {
                'cargo': cargo,
                'title': f'Excluir Cargo - {cargo.nome}',
                'action_url': 'administracao:cargos_excluir',
                'error': str(e)
            })
    
    return redirect('administracao:cargos_lista')