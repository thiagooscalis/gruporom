# -*- coding: utf-8 -*-
from django.urls import path
from core.views.administracao import usuarios

urlpatterns = [
    path('', usuarios.lista, name='usuarios_lista'),
    path('novo/modal/', usuarios.novo_modal, name='usuarios_novo_modal'),
    path('criar/', usuarios.criar, name='usuarios_criar'),
    path('<int:pk>/editar/modal/', usuarios.editar_modal, name='usuarios_editar_modal'),
    path('<int:pk>/atualizar/', usuarios.atualizar, name='usuarios_atualizar'),
    path('<int:pk>/excluir/modal/', usuarios.excluir_modal, name='usuarios_excluir_modal'),
    path('<int:pk>/excluir/', usuarios.excluir, name='usuarios_excluir'),
]