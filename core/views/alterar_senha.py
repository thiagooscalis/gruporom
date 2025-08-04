from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse
from core.forms import AlterarSenhaForm


@login_required
def alterar_senha_form(request):
    """Retorna o formulário de alteração de senha via HTMX"""
    form = AlterarSenhaForm(user=request.user)
    return render(request, 'partials/form_alterar_senha.html', {
        'form': form
    })


@login_required
def alterar_senha_submit(request):
    """Processa a alteração de senha via HTMX"""
    if request.method == 'POST':
        form = AlterarSenhaForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            # Salva a nova senha
            user = form.save()
            
            # Faz logout do usuário
            logout(request)
            
            # Retorna mensagem de sucesso com redirecionamento
            return render(request, 'partials/senha_alterada_sucesso.html')
        else:
            # Retorna o formulário com erros
            return render(request, 'partials/form_alterar_senha.html', {
                'form': form
            })
    
    # Se não for POST, redireciona para o formulário
    return alterar_senha_form(request)