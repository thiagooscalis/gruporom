# -*- coding: utf-8 -*-
from django.shortcuts import render
from core.decorators import comercial_required


@comercial_required
def home(request):
    """
    View principal da área comercial
    """
    context = {
        'title': 'Área Comercial',
    }
    
    return render(request, 'comercial/home.html', context)