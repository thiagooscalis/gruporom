from django.urls import path
from core.views.administracao import fornecedores

urlpatterns = [
    path('', fornecedores.lista, name='fornecedores_lista'),
    path('novo-modal/', fornecedores.novo_modal, name='fornecedores_novo_modal'),
    path('criar/', fornecedores.criar, name='fornecedores_criar'),
    path('<int:pk>/editar-modal/', fornecedores.editar_modal, name='fornecedores_editar_modal'),
    path('<int:pk>/atualizar/', fornecedores.atualizar, name='fornecedores_atualizar'),
    path('<int:pk>/excluir-modal/', fornecedores.excluir_modal, name='fornecedores_excluir_modal'),
    path('<int:pk>/excluir/', fornecedores.excluir, name='fornecedores_excluir'),
]