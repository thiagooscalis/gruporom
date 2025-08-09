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
from core.forms.contato import TelefoneFormSet, EmailFormSet
from core.utils.image_processing import crop_to_square, is_valid_image, needs_processing


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def lista(request):
    """
    View para listagem de pessoas
    """
    # Busca
    search = request.GET.get('search', '')
    tipo_filter = request.GET.get('tipo', '')
    
    # Query base
    pessoas = Pessoa.objects.all()
    
    # Aplica filtro de busca se houver
    if search:
        pessoas = pessoas.filter(
            Q(nome__icontains=search) |
            Q(doc__icontains=search) |
            Q(emails__email__icontains=search)
        )
    
    # Aplica filtro de tipo se houver
    if tipo_filter:
        if tipo_filter == 'pf':
            pessoas = pessoas.filter(tipo_doc='CPF')
        elif tipo_filter == 'pj':
            # PJ mas não empresa do Grupo ROM
            pessoas = pessoas.filter(tipo_doc='CNPJ', empresa_gruporom=False)
        elif tipo_filter == 'gruporom':
            pessoas = pessoas.filter(empresa_gruporom=True)
    
    # Ordenação
    pessoas = pessoas.order_by('nome')
    
    # Paginação
    paginator = Paginator(pessoas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'tipo_filter': tipo_filter,
        'restantes': page_obj.paginator.count - page_obj.end_index() if page_obj else 0,
    }
    
    # Se for requisição HTMX, verificar se é carregamento incremental
    if request.headers.get('HX-Request'):
        if request.GET.get('load_more'):
            # Carregamento incremental - retorna apenas as linhas
            return render(request, 'administracao/pessoas/partial_linhas.html', context)
        else:
            # Primeira carga ou filtro - retorna tabela completa
            return render(request, 'administracao/pessoas/partial_lista.html', context)
    
    return render(request, 'administracao/pessoas/lista.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def nova_modal(request):
    """
    View para retornar o modal de criação de pessoa via HTMX
    """
    form = PessoaForm()
    # Para formsets inline, precisa passar instance=None para criação
    telefone_formset = TelefoneFormSet(instance=None, prefix='telefones')
    email_formset = EmailFormSet(instance=None, prefix='emails')
    
    context = {
        'form': form,
        'telefone_formset': telefone_formset,
        'email_formset': email_formset,
    }
    return render(request, 'administracao/pessoas/modal_form_formsets.html', context)


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
        form = PessoaForm(request.POST, request.FILES)
        telefone_formset = TelefoneFormSet(request.POST, prefix='telefones')
        email_formset = EmailFormSet(request.POST, prefix='emails')
        
        if form.is_valid() and telefone_formset.is_valid() and email_formset.is_valid():
            pessoa = form.save()
            
            # Salva os telefones
            telefone_formset.instance = pessoa
            telefones = telefone_formset.save()
            
            # Salva os emails
            email_formset.instance = pessoa
            emails = email_formset.save()
            
            # Atualiza campos de compatibilidade (telefone e email principal)
            if telefones:
                # Pega o primeiro telefone ou o marcado como principal
                telefone_principal = next((t for t in telefones if t.principal), telefones[0])
                pessoa.telefone = telefone_principal.numero_completo
            
            if emails:
                # Pega o primeiro email ou o marcado como principal
                email_principal = next((e for e in emails if e.principal), emails[0])
                pessoa.email = email_principal.email
            
            pessoa.save()
            
            messages.success(request, f'Pessoa {pessoa.nome} criada com sucesso!')
            
            # Retorna um redirect HTMX para recarregar a página
            response = HttpResponse()
            response['HX-Redirect'] = request.META.get('HTTP_REFERER', '/administracao/pessoas/')
            return response
        else:
            # Retorna o formulário com erros
            context = {
                'form': form,
                'telefone_formset': telefone_formset,
                'email_formset': email_formset,
            }
            return render(request, 'administracao/pessoas/modal_form_formsets.html', context)
    
    return redirect('/administracao/pessoas/')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def editar_modal(request, pk):
    """
    View para retornar o modal de edição de pessoa via HTMX
    """
    pessoa = get_object_or_404(Pessoa, pk=pk)
    form = PessoaForm(instance=pessoa)
    telefone_formset = TelefoneFormSet(instance=pessoa, prefix='telefones')
    email_formset = EmailFormSet(instance=pessoa, prefix='emails')
    
    context = {
        'form': form,
        'pessoa': pessoa,
        'telefone_formset': telefone_formset,
        'email_formset': email_formset,
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
        form = PessoaForm(request.POST, request.FILES, instance=pessoa)
        telefone_formset = TelefoneFormSet(request.POST, instance=pessoa, prefix='telefones')
        email_formset = EmailFormSet(request.POST, instance=pessoa, prefix='emails')
        
        if form.is_valid() and telefone_formset.is_valid() and email_formset.is_valid():
            pessoa_atualizada = form.save()
            
            # Salva os telefones
            telefones = telefone_formset.save()
            
            # Salva os emails
            emails = email_formset.save()
            
            # Atualiza campos de compatibilidade (telefone e email principal)
            if telefones:
                # Pega o primeiro telefone ou o marcado como principal
                telefone_principal = next((t for t in telefones if t.principal), telefones[0] if telefones else None)
                if telefone_principal:
                    pessoa_atualizada.telefone = telefone_principal.numero_completo
            
            if emails:
                # Pega o primeiro email ou o marcado como principal
                email_principal = next((e for e in emails if e.principal), emails[0] if emails else None)
                if email_principal:
                    pessoa_atualizada.email = email_principal.email
            
            # Verifica se deve remover a cópia do passaporte
            if request.POST.get('remover_passaporte_copia'):
                if pessoa_atualizada.passaporte_copia:
                    # Remove o arquivo do storage
                    pessoa_atualizada.passaporte_copia.delete(save=False)
                    # Limpa o campo no banco
                    pessoa_atualizada.passaporte_copia = None
            
            pessoa_atualizada.save()
            
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
                'telefone_formset': telefone_formset,
                'email_formset': email_formset,
            }
            return render(request, 'administracao/pessoas/modal_edit_formsets.html', context)
    
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


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def foto_modal(request, pk):
    """
    View para retornar o modal de upload de foto via HTMX
    """
    pessoa = get_object_or_404(Pessoa, pk=pk)
    context = {
        'pessoa': pessoa,
    }
    return render(request, 'administracao/pessoas/modal_foto.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def foto_upload(request, pk):
    """
    View para processar o upload de foto com recorte automático
    """
    pessoa = get_object_or_404(Pessoa, pk=pk)
    
    if request.method == 'POST':
        foto = request.FILES.get('foto')
        
        if foto:
            try:
                # Validar imagem
                is_valid, error_message = is_valid_image(foto, max_size_mb=5)
                if not is_valid:
                    messages.error(request, error_message)
                    context = {'pessoa': pessoa}
                    return render(request, 'administracao/pessoas/modal_foto.html', context)
                
                # Reset file pointer após validação
                foto.seek(0)
                
                # Verificar se precisa de processamento
                processing_info = needs_processing(foto, max_size=800)
                
                if 'error' in processing_info:
                    messages.error(request, f'Erro ao analisar imagem: {processing_info["error"]}')
                    context = {'pessoa': pessoa}
                    return render(request, 'administracao/pessoas/modal_foto.html', context)
                
                # Remover foto antiga se existir
                if pessoa.foto:
                    pessoa.foto.delete(save=False)
                
                if processing_info['needs_any_processing']:
                    # Processar imagem (recorte/otimização necessária)
                    try:
                        processed_image = crop_to_square(foto, quality=85, max_size=800)
                        
                        # Salvar nova foto processada
                        pessoa.foto.save(
                            processed_image.name,
                            processed_image,
                            save=True
                        )
                        
                        # Mensagem específica baseada no que foi processado
                        if processing_info['needs_crop']:
                            messages.success(request, f'Foto de {pessoa.nome} atualizada com sucesso! Imagem foi automaticamente recortada para formato quadrado.')
                        else:
                            messages.success(request, f'Foto de {pessoa.nome} atualizada com sucesso! Imagem foi otimizada.')
                        
                    except ValueError as e:
                        messages.error(request, f'Erro ao processar imagem: {str(e)}')
                        context = {'pessoa': pessoa}
                        return render(request, 'administracao/pessoas/modal_foto.html', context)
                else:
                    # Imagem já está perfeita, salvar diretamente
                    pessoa.foto = foto
                    pessoa.save()
                    
                    messages.success(request, f'Foto de {pessoa.nome} atualizada com sucesso! Imagem já estava no formato ideal.')
                
            except Exception as e:
                messages.error(request, f'Erro inesperado ao processar arquivo: {str(e)}')
                context = {'pessoa': pessoa}
                return render(request, 'administracao/pessoas/modal_foto.html', context)
            
            # Retorna um redirect HTMX para recarregar a página
            response = HttpResponse()
            response['HX-Redirect'] = request.META.get('HTTP_REFERER', '/administracao/pessoas/')
            return response
        else:
            messages.error(request, 'Nenhum arquivo foi selecionado.')
            context = {'pessoa': pessoa}
            return render(request, 'administracao/pessoas/modal_foto.html', context)
    
    return redirect('/administracao/pessoas/')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def foto_remover(request, pk):
    """
    View para remover a foto da pessoa
    """
    pessoa = get_object_or_404(Pessoa, pk=pk)
    
    if request.method == 'POST':
        if pessoa.foto:
            # Remove o arquivo físico
            pessoa.foto.delete(save=False)
            # Remove a referência do banco
            pessoa.foto = None
            pessoa.save()
            
            messages.success(request, f'Foto de {pessoa.nome} removida com sucesso!')
        else:
            messages.warning(request, f'{pessoa.nome} não possui foto para remover.')
        
        # Retorna um redirect HTMX para recarregar a página
        response = HttpResponse()
        response['HX-Redirect'] = request.META.get('HTTP_REFERER', '/administracao/pessoas/')
        return response
    
    return redirect('/administracao/pessoas/')