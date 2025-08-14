from django.shortcuts import render
from core.decorators import operacional_required


@operacional_required
def home(request):
    """
    Dashboard principal da área operacional
    """
    context = {
        'area_atual': 'operacional',
        'titulo': 'Dashboard Operacional',
    }
    
    return render(request, 'operacional/home.html', context)