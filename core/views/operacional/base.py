from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test


def is_operacional_user(user):
    """
    Verifica se o usuário pertence ao grupo Operacional
    """
    return user.is_authenticated and user.groups.filter(name='Operacional').exists()


@user_passes_test(is_operacional_user, login_url='/login/')
def home(request):
    """
    Dashboard principal da área operacional
    """
    context = {
        'area_atual': 'operacional',
        'titulo': 'Dashboard Operacional',
    }
    
    return render(request, 'operacional/home.html', context)