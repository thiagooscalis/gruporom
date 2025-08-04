from django.urls import path
from core.views.administracao import turnos

urlpatterns = [
    path('', turnos.lista, name='turnos_lista'),
    path('novo-modal/', turnos.novo_modal, name='turnos_novo_modal'),
    path('criar/', turnos.criar, name='turnos_criar'),
    path('<int:pk>/editar-modal/', turnos.editar_modal, name='turnos_editar_modal'),
    path('<int:pk>/atualizar/', turnos.atualizar, name='turnos_atualizar'),
    path('<int:pk>/excluir-modal/', turnos.excluir_modal, name='turnos_excluir_modal'),
    path('<int:pk>/excluir/', turnos.excluir, name='turnos_excluir'),
]