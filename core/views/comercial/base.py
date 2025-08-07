# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def home(request):
    """
    View principal da área comercial
    """
    context = {
        'title': 'Área Comercial',
    }
    
    return render(request, 'comercial/home.html', context)