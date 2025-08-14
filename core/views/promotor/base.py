# -*- coding: utf-8 -*-
from django.shortcuts import render
from core.decorators import promotor_required


@promotor_required
def home_view(request):
    """
    View principal da área promotor
    """
    context = {
        'title': 'Área Promotor',
    }
    
    return render(request, 'promotor/home.html', context)