# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse
from django.db.models.deletion import ProtectedError
from core.models import Pessoa
from core.forms.pessoa import PessoaForm


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def lista(request):
    """
    View para listagem de pessoas
    """
    # Busca
    search = request.GET.get('search', '')
    
    # Query base
    pessoas = Pessoa.objects.all()
    
    # Aplica filtro de busca se houver
    if search:
        pessoas = pessoas.filter(
            Q(nome__icontains=search) |
            Q(doc__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Ordenação
    pessoas = pessoas.order_by('nome')
    
    # Paginação
    paginator = Paginator(pessoas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    
    return render(request, 'administracao/pessoas/lista.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def nova_modal(request):
    """
    View para retornar o modal de criação de pessoa via HTMX
    """
    form = PessoaForm()
    context = {
        'form': form,
    }
    return render(request, 'administracao/pessoas/modal_form.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def nova_modal_simples(request):
    """
    View para retornar o modal simplificado de criação de pessoa
    Usado quando chamado de outro modal (ex: usuários)
    """
    form = PessoaForm()
    context = {
        'form': form,
    }
    return render(request, 'administracao/pessoas/modal_form_simples.html', context)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def criar(request):
    """
    View para processar o formulário de criação de pessoa
    """
    if request.method == 'POST':
        form = PessoaForm(request.POST)
        
        if form.is_valid():
            pessoa = form.save()
            messages.success(request, f'Pessoa {pessoa.nome} criada com sucesso!')
            
            # Retorna um redirect HTMX para recarregar a página
            response = HttpResponse()
            response['HX-Redirect'] = request.META.get('HTTP_REFERER', '/administracao/pessoas/')
            return response
        else:
            # Retorna o formulário com erros
            context = {
                'form': form,
                    }
            return render(request, 'administracao/pessoas/modal_form.html', context)
    
    return redirect('/administracao/pessoas/')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def editar_modal(request, pk):
    """
    View para retornar o modal de edição de pessoa via HTMX
    """
    pessoa = get_object_or_404(Pessoa, pk=pk)
    form = PessoaForm(instance=pessoa)
    context = {
        'form': form,
        'pessoa': pessoa,
    }
    return render(request, 'administracao/pessoas/modal_edit.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def atualizar(request, pk):
    """
    View para processar o formulário de edição de pessoa
    """
    pessoa = get_object_or_404(Pessoa, pk=pk)
    
    if request.method == 'POST':
        form = PessoaForm(request.POST, instance=pessoa)
        if form.is_valid():
            pessoa_atualizada = form.save()
            messages.success(request, f'Pessoa {pessoa_atualizada.nome} atualizada com sucesso!')
            
            # Retorna um redirect HTMX para recarregar a página
            response = HttpResponse()
            response['HX-Redirect'] = request.META.get('HTTP_REFERER', '/administracao/pessoas/')
            return response
        else:
            # Retorna o formulário com erros
            context = {
                'form': form,
                'pessoa': pessoa,
                    }
            return render(request, 'administracao/pessoas/modal_edit.html', context)
    
    return redirect('/administracao/pessoas/')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def excluir_modal(request, pk):
    """
    View para retornar o modal de confirmação de exclusão via HTMX
    """
    pessoa = get_object_or_404(Pessoa, pk=pk)
    
    # Verifica se a pessoa está vinculada a um usuário
    tem_usuario = hasattr(pessoa, 'usuario')
    
    context = {
        'pessoa': pessoa,
        'tem_usuario': tem_usuario,
    }
    return render(request, 'administracao/pessoas/modal_delete.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def excluir(request, pk):
    """
    View para processar a exclusão de pessoa
    """
    pessoa = get_object_or_404(Pessoa, pk=pk)
    
    if request.method == 'POST':
        nome_pessoa = pessoa.nome
        try:
            pessoa.delete()
            messages.success(request, f'Pessoa {nome_pessoa} excluída com sucesso!')
        except ProtectedError:
            messages.error(request, f'Não é possível excluir {nome_pessoa} pois está vinculada a um usuário do sistema.')
        
        # Retorna um redirect HTMX para recarregar a página
        response = HttpResponse()
        response['HX-Redirect'] = request.META.get('HTTP_REFERER', '/administracao/pessoas/')
        return response
    
    return redirect('/administracao/pessoas/')