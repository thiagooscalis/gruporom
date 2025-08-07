# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse
from django.db.models.deletion import ProtectedError
from django.urls import reverse
from core.models import Usuario, Pessoa
from core.forms.usuario import UsuarioForm


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def lista(request):
    """
    View para listagem de usuários
    """
    # Busca
    search = request.GET.get('search', '')
    
    # Query base
    usuarios = Usuario.objects.select_related('pessoa').all()
    
    # Aplica filtro de busca se houver
    if search:
        usuarios = usuarios.filter(
            Q(username__icontains=search) |
            Q(pessoa__nome__icontains=search) |
            Q(pessoa__email__icontains=search)
        )
    
    # Ordenação
    usuarios = usuarios.order_by('pessoa__nome')
    
    # Paginação
    paginator = Paginator(usuarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    
    return render(request, 'administracao/usuarios/lista.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def novo_modal(request):
    """
    View para retornar o modal de criação de usuário via HTMX
    """
    form = UsuarioForm()
    context = {
        'form': form,
        'buscar_pessoas_url': reverse('buscar_pessoas', kwargs={'area': 'administracao'}),
    }
    return render(request, 'administracao/usuarios/modal_form.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def criar(request):
    """
    View para processar o formulário de criação de usuário
    """
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuário {usuario.username} criado com sucesso!')
            
            # Retorna um redirect HTMX para recarregar a página
            response = HttpResponse()
            response['HX-Redirect'] = request.META.get('HTTP_REFERER', '/administracao/usuarios/')
            return response
        else:
            # Retorna apenas o conteúdo do formulário com erros
            context = {
                'form': form,
                'buscar_pessoas_url': reverse('buscar_pessoas', kwargs={'area': 'administracao'}),
            }
            return render(request, 'administracao/usuarios/form_content.html', context)
    
    return redirect('/administracao/usuarios/')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def editar_modal(request, pk):
    """
    View para retornar o modal de edição de usuário via HTMX
    """
    usuario = get_object_or_404(Usuario, pk=pk)
    form = UsuarioForm(instance=usuario)
    
    # Se for o próprio usuário, desabilita o campo is_active
    if request.user.pk == usuario.pk:
        form.fields['is_active'].widget.attrs['disabled'] = True
        form.fields['is_active'].help_text = "Você não pode desativar seu próprio usuário"
    
    context = {
        'form': form,
        'usuario': usuario,
        'e_proprio_usuario': request.user.pk == usuario.pk,
        'buscar_pessoas_edicao_url': reverse('buscar_pessoas_edicao', kwargs={'area': 'administracao'}),
        'usuario_id_param': f'#usuario-id-{usuario.pk}',
    }
    return render(request, 'administracao/usuarios/modal_edit.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def atualizar(request, pk):
    """
    View para processar o formulário de edição de usuário
    """
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        
        # Se for o próprio usuário, força is_active como True
        if request.user.pk == usuario.pk and form.is_valid():
            usuario_temp = form.save(commit=False)
            usuario_temp.is_active = True
            usuario_temp.save()
            form.save_m2m()
            messages.success(request, f'Usuário {usuario_temp.username} atualizado com sucesso!')
            
            # Retorna um redirect HTMX para recarregar a página
            response = HttpResponse()
            response['HX-Redirect'] = request.META.get('HTTP_REFERER', '/administracao/usuarios/')
            return response
        elif form.is_valid():
            usuario_atualizado = form.save()
            messages.success(request, f'Usuário {usuario_atualizado.username} atualizado com sucesso!')
            
            # Retorna um redirect HTMX para recarregar a página
            response = HttpResponse()
            response['HX-Redirect'] = request.META.get('HTTP_REFERER', '/administracao/usuarios/')
            return response
        else:
            # Se for o próprio usuário, desabilita o campo is_active novamente
            if request.user.pk == usuario.pk:
                form.fields['is_active'].widget.attrs['disabled'] = True
                form.fields['is_active'].help_text = "Você não pode desativar seu próprio usuário"
            
            # Retorna o formulário com erros
            context = {
                'form': form,
                'usuario': usuario,
                'e_proprio_usuario': request.user.pk == usuario.pk,
                'buscar_pessoas_edicao_url': reverse('buscar_pessoas_edicao', kwargs={'area': 'administracao'}),
                'usuario_id_param': f'#usuario-id-{usuario.pk}',
            }
            return render(request, 'administracao/usuarios/modal_edit.html', context)
    
    return redirect('/administracao/usuarios/')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def excluir_modal(request, pk):
    """
    View para retornar o modal de confirmação de exclusão via HTMX
    """
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Impede que o usuário exclua a si mesmo
    e_proprio_usuario = request.user.pk == usuario.pk
    
    context = {
        'usuario': usuario,
        'e_proprio_usuario': e_proprio_usuario,
    }
    return render(request, 'administracao/usuarios/modal_delete.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def excluir(request, pk):
    """
    View para processar a exclusão de usuário
    """
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        # Impede que o usuário exclua a si mesmo
        if request.user.pk == usuario.pk:
            messages.error(request, 'Você não pode excluir seu próprio usuário.')
        else:
            username = usuario.username
            try:
                usuario.delete()
                messages.success(request, f'Usuário {username} excluído com sucesso!')
            except ProtectedError:
                messages.error(request, f'Não é possível excluir o usuário {username} pois possui dados relacionados.')
        
        # Retorna um redirect HTMX para recarregar a página
        response = HttpResponse()
        response['HX-Redirect'] = request.META.get('HTTP_REFERER', '/administracao/usuarios/')
        return response
    
    return redirect('/administracao/usuarios/')