# -*- coding: utf-8 -*-
from django.urls import path
from core.views.administracao import pessoas

urlpatterns = [
    path('', pessoas.lista, name='pessoas_lista'),
    path('nova/modal/', pessoas.nova_modal, name='pessoas_nova_modal'),
    path('nova/modal/simples/', pessoas.nova_modal_simples, name='pessoas_nova_modal_simples'),
    path('criar/', pessoas.criar, name='pessoas_criar'),
    path('<int:pk>/editar/modal/', pessoas.editar_modal, name='pessoas_editar_modal'),
    path('<int:pk>/atualizar/', pessoas.atualizar, name='pessoas_atualizar'),
    path('<int:pk>/excluir/modal/', pessoas.excluir_modal, name='pessoas_excluir_modal'),
    path('<int:pk>/excluir/', pessoas.excluir, name='pessoas_excluir'),
    path('<int:pk>/foto/modal/', pessoas.foto_modal, name='pessoas_foto_modal'),
    path('<int:pk>/foto/upload/', pessoas.foto_upload, name='pessoas_foto_upload'),
    path('<int:pk>/foto/remover/', pessoas.foto_remover, name='pessoas_foto_remover'),
]