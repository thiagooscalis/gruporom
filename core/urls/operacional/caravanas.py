# -*- coding: utf-8 -*-
from django.urls import path
from core.views.operacional import caravanas

urlpatterns = [
    path('', caravanas.caravanas_lista, name='caravanas_lista'),
    path('criar/', caravanas.caravana_criar_modal, name='caravana_criar'),
    path('<int:pk>/', caravanas.caravana_detalhes, name='caravana_detalhes'),
    path('<int:pk>/editar/', caravanas.caravana_editar_modal, name='caravana_editar'),
    path('<int:pk>/excluir/', caravanas.caravana_excluir_modal, name='caravana_excluir'),
]