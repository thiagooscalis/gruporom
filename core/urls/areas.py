# -*- coding: utf-8 -*-
from django.urls import path
from core.views.pessoas import buscar_pessoas, buscar_pessoas_para_edicao

# URLs globais que funcionam em todas as áreas com o parâmetro area
urlpatterns = [
    # APIs de busca
    path('<slug:area>/buscar-pessoas/', buscar_pessoas, name='buscar_pessoas'),
    path('<slug:area>/buscar-pessoas-edicao/', buscar_pessoas_para_edicao, name='buscar_pessoas_edicao'),
]