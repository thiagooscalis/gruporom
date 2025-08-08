# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Promotor').exists())
def home_view(request):
    """
    View principal da área promotor
    """
    context = {
        'title': 'Área Promotor',
    }
    
    return render(request, 'promotor/home.html', context)