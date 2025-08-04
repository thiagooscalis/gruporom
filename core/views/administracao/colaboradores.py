# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from core.models import Colaborador
from core.forms import ColaboradorForm


@login_required
def lista(request):
    """Lista todos os colaboradores com busca e paginação"""
    search = request.GET.get('search', '')
    
    colaboradores = Colaborador.objects.select_related(
        'pessoa', 'cargo', 'cargo__empresa'
    ).prefetch_related('turnos')
    
    if search:
        colaboradores = colaboradores.filter(
            Q(pessoa__nome__icontains=search) |
            Q(pessoa__cpf__icontains=search) |
            Q(pessoa__cnpj__icontains=search) |
            Q(cargo__nome__icontains=search) |
            Q(cargo__empresa__nome__icontains=search)
        )
    
    paginator = Paginator(colaboradores, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'area': 'administracao'
    }
    
    return render(request, 'administracao/colaboradores/lista.html', context)


@login_required
def novo_modal(request):
    """Retorna o modal para criar novo colaborador via HTMX"""
    form = ColaboradorForm()
    return render(request, 'administracao/colaboradores/modal_form.html', {
        'form': form,
        'title': 'Novo Colaborador',
        'action_url': 'administracao:colaboradores_criar',
        'buscar_pessoas_url': reverse('buscar_pessoas', kwargs={'area': 'administracao'}) + '?all=true'
    })


@login_required
def criar(request):
    """Cria novo colaborador via HTMX"""
    if request.method == 'POST':
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            try:
                colaborador = form.save()
                messages.success(request, f'Colaborador "{colaborador.nome}" criado com sucesso!')
                
                # Retorna script para fechar modal e recarregar página
                return HttpResponse("""
                    <script>
                        const modal = bootstrap.Modal.getInstance(document.getElementById('modalColaborador'));
                        if (modal) modal.hide();
                        window.location.reload();
                    </script>
                """)
            except Exception as e:
                form.add_error(None, f'Erro ao salvar: {str(e)}')
        
        # Retorna formulário com erros
        return render(request, 'administracao/colaboradores/modal_form.html', {
            'form': form,
            'title': 'Novo Colaborador',
            'action_url': 'administracao:colaboradores_criar',
            'buscar_pessoas_url': reverse('buscar_pessoas', kwargs={'area': 'administracao'}) + '?all=true'
        })
    
    return redirect('administracao:colaboradores_lista')


@login_required
def editar_modal(request, pk):
    """Retorna o modal para editar colaborador via HTMX"""
    colaborador = get_object_or_404(Colaborador, pk=pk)
    form = ColaboradorForm(instance=colaborador)
    return render(request, 'administracao/colaboradores/modal_form.html', {
        'form': form,
        'title': f'Editar Colaborador - {colaborador.nome}',
        'action_url': 'administracao:colaboradores_atualizar',
        'colaborador_id': colaborador.id,
        'buscar_pessoas_url': reverse('buscar_pessoas', kwargs={'area': 'administracao'}) + '?all=true'
    })


@login_required
def atualizar(request, pk):
    """Atualiza colaborador via HTMX"""
    colaborador = get_object_or_404(Colaborador, pk=pk)
    
    if request.method == 'POST':
        form = ColaboradorForm(request.POST, instance=colaborador)
        if form.is_valid():
            try:
                colaborador = form.save()
                messages.success(request, f'Colaborador "{colaborador.nome}" atualizado com sucesso!')
                
                # Retorna script para fechar modal e recarregar página
                return HttpResponse("""
                    <script>
                        const modal = bootstrap.Modal.getInstance(document.getElementById('modalColaborador'));
                        if (modal) modal.hide();
                        window.location.reload();
                    </script>
                """)
            except Exception as e:
                form.add_error(None, f'Erro ao salvar: {str(e)}')
        
        # Retorna formulário com erros
        return render(request, 'administracao/colaboradores/modal_form.html', {
            'form': form,
            'title': f'Editar Colaborador - {colaborador.nome}',
            'action_url': 'administracao:colaboradores_atualizar',
            'colaborador_id': colaborador.id,
            'buscar_pessoas_url': reverse('buscar_pessoas', kwargs={'area': 'administracao'}) + '?all=true'
        })
    
    return redirect('administracao:colaboradores_lista')


@login_required
def excluir_modal(request, pk):
    """Retorna o modal para confirmar exclusão do colaborador via HTMX"""
    colaborador = get_object_or_404(Colaborador, pk=pk)
    return render(request, 'administracao/colaboradores/modal_excluir.html', {
        'colaborador': colaborador,
        'title': f'Excluir Colaborador - {colaborador.nome}',
        'action_url': 'administracao:colaboradores_excluir',
    })


@login_required
def excluir(request, pk):
    """Exclui colaborador via HTMX"""
    colaborador = get_object_or_404(Colaborador, pk=pk)
    
    if request.method == 'POST':
        try:
            nome_colaborador = colaborador.nome
            colaborador.delete()
            messages.success(request, f'Colaborador "{nome_colaborador}" excluído com sucesso!')
            
            # Retorna script para fechar modal e recarregar página
            return HttpResponse("""
                <script>
                    const modal = bootstrap.Modal.getInstance(document.getElementById('modalColaborador'));
                    if (modal) modal.hide();
                    window.location.reload();
                </script>
            """)
        except Exception as e:
            messages.error(request, f'Erro ao excluir colaborador: {str(e)}')
            return render(request, 'administracao/colaboradores/modal_excluir.html', {
                'colaborador': colaborador,
                'title': f'Excluir Colaborador - {colaborador.nome}',
                'action_url': 'administracao:colaboradores_excluir',
                'error': str(e)
            })
    
    return redirect('administracao:colaboradores_lista')