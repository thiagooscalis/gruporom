# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.models import Group
from core.models import Usuario, Pessoa
from core.decorators import administracao_required


@administracao_required
def home(request):
    """
    View principal do painel de administracao
    """
    # Coleta estatisticas para o dashboard
    context = {
        'total_usuarios': Usuario.objects.count(),
        'total_pessoas': Pessoa.objects.count(),
        'total_grupos': Group.objects.count(),
    }
    
    return render(request, 'administracao/home.html', context)