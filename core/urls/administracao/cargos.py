from django.urls import path
from core.views.administracao import cargos

urlpatterns = [
    path('', cargos.lista, name='cargos_lista'),
    path('novo-modal/', cargos.novo_modal, name='cargos_novo_modal'),
    path('criar/', cargos.criar, name='cargos_criar'),
    path('<int:pk>/editar-modal/', cargos.editar_modal, name='cargos_editar_modal'),
    path('<int:pk>/atualizar/', cargos.atualizar, name='cargos_atualizar'),
    path('<int:pk>/excluir-modal/', cargos.excluir_modal, name='cargos_excluir_modal'),
    path('<int:pk>/excluir/', cargos.excluir, name='cargos_excluir'),
]