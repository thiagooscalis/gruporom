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
    """Lista todos os fornecedores com busca e paginação"""
    search = request.GET.get('search', '')
    
    fornecedores = Fornecedor.objects.select_related('pessoa').all()
    
    if search:
        fornecedores = fornecedores.filter(
            Q(pessoa__nome__icontains=search) |
            Q(pessoa__doc__icontains=search) |
            Q(pessoa__email__icontains=search) |
            Q(tipo_empresa__icontains=search)
        )
    
    paginator = Paginator(fornecedores, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'area': 'administracao'
    }
    
    return render(request, 'administracao/fornecedores/lista.html', context)


@login_required
def novo_modal(request):
    """Retorna o modal para criar novo fornecedor via HTMX"""
    form = FornecedorForm()
    return render(request, 'administracao/fornecedores/modal_form.html', {
        'form': form,
        'title': 'Novo Fornecedor',
        'action_url': 'administracao:fornecedores_criar',
        'buscar_pessoas_url': reverse('buscar_pessoas', kwargs={'area': 'administracao'}) + '?all=true'
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
                        const modal = bootstrap.Modal.getInstance(document.getElementById('modalFornecedor'));
                        if (modal) modal.hide();
                        window.location.reload();
                    </script>
                """)
            except Exception as e:
                form.add_error(None, f'Erro ao salvar: {str(e)}')
        
        # Retorna formulário com erros
        return render(request, 'administracao/fornecedores/modal_form.html', {
            'form': form,
            'title': 'Novo Fornecedor',
            'action_url': 'administracao:fornecedores_criar',
            'buscar_pessoas_url': reverse('buscar_pessoas', kwargs={'area': 'administracao'}) + '?all=true'
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
                    const modal = bootstrap.Modal.getInstance(document.getElementById('modalFornecedor'));
                    if (modal) modal.hide();
                    window.location.reload();
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
        'buscar_pessoas_url': reverse('buscar_pessoas', kwargs={'area': 'administracao'}) + '?all=true'
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
                        const modal = bootstrap.Modal.getInstance(document.getElementById('modalFornecedor'));
                        if (modal) modal.hide();
                        window.location.reload();
                    </script>
                """)
            except Exception as e:
                form.add_error(None, f'Erro ao salvar: {str(e)}')
        
        # Retorna formulário com erros
        return render(request, 'administracao/fornecedores/modal_form.html', {
            'form': form,
            'title': f'Editar Fornecedor - {fornecedor.pessoa.nome}',
            'action_url': 'administracao:fornecedores_atualizar',
            'fornecedor_id': fornecedor.id,
            'buscar_pessoas_url': reverse('buscar_pessoas', kwargs={'area': 'administracao'}) + '?all=true'
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
                    const modal = bootstrap.Modal.getInstance(document.getElementById('modalFornecedor'));
                    if (modal) modal.hide();
                    window.location.reload();
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
