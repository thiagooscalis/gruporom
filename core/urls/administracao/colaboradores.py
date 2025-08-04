from django.urls import path
from core.views.administracao import colaboradores

urlpatterns = [
    path('', colaboradores.lista, name='colaboradores_lista'),
    path('novo-modal/', colaboradores.novo_modal, name='colaboradores_novo_modal'),
    path('criar/', colaboradores.criar, name='colaboradores_criar'),
    path('<int:pk>/editar-modal/', colaboradores.editar_modal, name='colaboradores_editar_modal'),
    path('<int:pk>/atualizar/', colaboradores.atualizar, name='colaboradores_atualizar'),
    path('<int:pk>/excluir-modal/', colaboradores.excluir_modal, name='colaboradores_excluir_modal'),
    path('<int:pk>/excluir/', colaboradores.excluir, name='colaboradores_excluir'),
]