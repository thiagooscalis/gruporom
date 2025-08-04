# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from core.models import Usuario, Pessoa
from core.decorators import group_area_required




@login_required
@group_area_required
def home(request):
    """
    View principal do painel de administracao
    """
    # Coleta estatisticas para o dashboard
    context = {
        'area': request.area,  # Área extraída automaticamente pelo decorator
        'total_usuarios': Usuario.objects.count(),
        'total_pessoas': Pessoa.objects.count(),
        'total_grupos': Group.objects.count(),
    }
    
    return render(request, 'administracao/home.html', context)