from django.urls import path, include

app_name = 'administracao'

urlpatterns = [
    path('', include('core.urls.administracao.base')),
    path('pessoas/', include('core.urls.administracao.pessoas')),
    path('usuarios/', include('core.urls.administracao.usuarios')),
    path('fornecedores/', include('core.urls.administracao.fornecedores')),
]