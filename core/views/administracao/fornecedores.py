from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from core.models import Fornecedor
from core.forms import FornecedorForm


@login_required
def lista(request):
    """Lista todos os fornecedores com busca e paginação moderna"""
    search = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    load_more = request.GET.get('load_more')
    
    fornecedores = Fornecedor.objects.select_related('pessoa').all()
    
    if search:
        fornecedores = fornecedores.filter(
            Q(pessoa__nome__icontains=search) |
            Q(pessoa__doc__icontains=search) |
            Q(pessoa__email1__icontains=search) |
            Q(tipo_empresa__icontains=search)
        )
    
    # Paginação com 20 itens por página
    paginator = Paginator(fornecedores, 20)
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
            return render(request, 'administracao/fornecedores/partial_linhas.html', context)
        else:
            return render(request, 'administracao/fornecedores/partial_lista.html', context)
    
    return render(request, 'administracao/fornecedores/lista.html', context)


@login_required
def novo_modal(request):
    """Retorna o modal para criar novo fornecedor via HTMX"""
    form = FornecedorForm()
    return render(request, 'administracao/fornecedores/modal_form.html', {
        'form': form,
        'title': 'Novo Fornecedor',
        'action_url': 'administracao:fornecedores_criar'
    })


@login_required
def criar(request):
    """Cria novo fornecedor via HTMX"""
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            try:
                from django.db import transaction
                with transaction.atomic():
                    fornecedor = form.save()
                
                messages.success(request, f'Fornecedor "{fornecedor.pessoa.nome}" criado com sucesso!')
                
                # Retorna script para fechar modal e recarregar página
                return HttpResponse("""
                    <script>
                        // Fechar modal Alpine.js e recarregar listagem
                        document.querySelector('.modal-backdrop')?.remove();
                        document.querySelector('[x-data]')?.$el?.remove();
                        // Recarregar container da listagem via HTMX
                        htmx.ajax('GET', '/administracao/fornecedores/', '#fornecedores-container');
                    </script>
                """)
            except Exception as e:
                form.add_error(None, f'Erro ao salvar: {str(e)}')
        
        # Retorna formulário com wrapper para HTMX
        return render(request, 'administracao/fornecedores/form_with_wrapper.html', {
            'form': form,
            'action_url': 'administracao:fornecedores_criar'
        })
    
    return redirect('administracao:fornecedores_lista')


@login_required
def excluir_modal(request, pk):
    """Retorna o modal para confirmar exclusão do fornecedor via HTMX"""
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    return render(request, 'administracao/fornecedores/modal_excluir.html', {
        'fornecedor': fornecedor,
        'title': f'Excluir Fornecedor - {fornecedor.pessoa.nome}',
        'action_url': 'administracao:fornecedores_excluir',
    })


@login_required
def excluir(request, pk):
    """Exclui fornecedor via HTMX"""
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    
    if request.method == 'POST':
        try:
            nome_fornecedor = fornecedor.pessoa.nome
            fornecedor.delete()
            messages.success(request, f'Fornecedor "{nome_fornecedor}" excluído com sucesso!')
            
            # Retorna script para fechar modal e recarregar página
            return HttpResponse("""
                <script>
                    // Fechar modal Alpine.js e recarregar listagem
                    document.querySelector('.modal-backdrop')?.remove();
                    document.querySelector('[x-data]')?.$el?.remove();
                    // Recarregar container da listagem via HTMX
                    htmx.ajax('GET', '/administracao/fornecedores/', '#fornecedores-container');
                </script>
            """)
        except Exception as e:
            messages.error(request, f'Erro ao excluir fornecedor: {str(e)}')
            return render(request, 'administracao/fornecedores/modal_excluir.html', {
                'fornecedor': fornecedor,
                'title': f'Excluir Fornecedor - {fornecedor.pessoa.nome}',
                'action_url': 'administracao:fornecedores_excluir',
                'error': str(e)
            })
    
    return redirect('administracao:fornecedores_lista')


@login_required
def editar_modal(request, pk):
    """Retorna o modal para editar fornecedor via HTMX"""
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    form = FornecedorForm(instance=fornecedor)
    return render(request, 'administracao/fornecedores/modal_form.html', {
        'form': form,
        'title': f'Editar Fornecedor - {fornecedor.pessoa.nome}',
        'action_url': 'administracao:fornecedores_atualizar',
        'fornecedor_id': fornecedor.id,
    })


@login_required
def atualizar(request, pk):
    """Atualiza fornecedor via HTMX"""
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    
    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
            try:
                from django.db import transaction
                with transaction.atomic():
                    fornecedor = form.save()
                
                messages.success(request, f'Fornecedor "{fornecedor.pessoa.nome}" atualizado com sucesso!')
                
                # Retorna script para fechar modal e recarregar página
                return HttpResponse("""
                    <script>
                        // Fechar modal Alpine.js e recarregar listagem
                        document.querySelector('.modal-backdrop')?.remove();
                        document.querySelector('[x-data]')?.$el?.remove();
                        // Recarregar container da listagem via HTMX
                        htmx.ajax('GET', '/administracao/fornecedores/', '#fornecedores-container');
                    </script>
                """)
            except Exception as e:
                form.add_error(None, f'Erro ao salvar: {str(e)}')
        
        # Retorna formulário com wrapper para HTMX
        return render(request, 'administracao/fornecedores/form_with_wrapper.html', {
            'form': form,
            'action_url': 'administracao:fornecedores_atualizar',
            'fornecedor_id': fornecedor.id
        })
    
    return redirect('administracao:fornecedores_lista')

