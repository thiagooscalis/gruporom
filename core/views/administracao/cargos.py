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
    """Lista todos os cargos com busca e paginação moderna"""
    search = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    load_more = request.GET.get('load_more')
    
    cargos = Cargo.objects.select_related('empresa').all()
    
    if search:
        cargos = cargos.filter(
            Q(nome__icontains=search) |
            Q(empresa__nome__icontains=search)
        )
    
    # Paginação com 20 itens por página
    paginator = Paginator(cargos, 20)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'restantes': page_obj.paginator.count - page_obj.end_index() if page_obj else 0,
        'area': 'administracao'
    }
    
    # HTMX Detection
    if request.headers.get('HX-Request'):
        if load_more:
            return render(request, 'administracao/cargos/partial_linhas.html', context)
        else:
            return render(request, 'administracao/cargos/partial_lista.html', context)
    
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
                from django.db import transaction
                with transaction.atomic():
                    cargo = form.save()
                
                messages.success(request, f'Cargo "{cargo.nome}" criado com sucesso!')
                
                # Retorna script para fechar modal e recarregar página
                return HttpResponse("""
                    <script>
                        // Fechar modal Alpine.js
                        const modal = document.querySelector('[x-data]');
                        if (modal && modal.__x) {
                            modal.__x.$data.close();
                        } else {
                            // Fallback para remoção direta
                            document.querySelector('.fixed.inset-0.bg-black')?.remove();
                        }
                        // Recarregar container da listagem via HTMX
                        htmx.ajax('GET', '/administracao/cargos/', '#cargos-container');
                    </script>
                """)
            except Exception as e:
                form.add_error(None, f'Erro ao salvar: {str(e)}')
        
        # Retorna formulário com wrapper para HTMX
        return render(request, 'administracao/cargos/form_with_wrapper.html', {
            'form': form,
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
                from django.db import transaction
                with transaction.atomic():
                    cargo = form.save()
                
                messages.success(request, f'Cargo "{cargo.nome}" atualizado com sucesso!')
                
                # Retorna script para fechar modal e recarregar página
                return HttpResponse("""
                    <script>
                        // Fechar modal Alpine.js
                        const modal = document.querySelector('[x-data]');
                        if (modal && modal.__x) {
                            modal.__x.$data.close();
                        } else {
                            // Fallback para remoção direta
                            document.querySelector('.fixed.inset-0.bg-black')?.remove();
                        }
                        // Recarregar container da listagem via HTMX
                        htmx.ajax('GET', '/administracao/cargos/', '#cargos-container');
                    </script>
                """)
            except Exception as e:
                form.add_error(None, f'Erro ao salvar: {str(e)}')
        
        # Retorna formulário com wrapper para HTMX
        return render(request, 'administracao/cargos/form_with_wrapper.html', {
            'form': form,
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
                    // Fechar modal Alpine.js
                    const modal = document.querySelector('[x-data]');
                    if (modal && modal.__x) {
                        modal.__x.$data.close();
                    } else {
                        // Fallback para remoção direta
                        document.querySelector('.fixed.inset-0.bg-black')?.remove();
                    }
                    // Recarregar container da listagem via HTMX
                    htmx.ajax('GET', '/administracao/cargos/', '#cargos-container');
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