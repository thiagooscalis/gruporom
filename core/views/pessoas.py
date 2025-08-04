# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from core.models import Pessoa
from core.decorators import group_area_required


@login_required
@group_area_required
def buscar_pessoas(request, area):
    """
    API para busca de pessoas via HTMX autocomplete
    Retorna pessoas disponíveis (sem usuário vinculado)
    """
    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        # Não busca com menos de 2 caracteres
        return render(
            request, "components/pessoas_autocomplete.html", {"pessoas": []}
        )

    # Busca pessoas sem usuário
    pessoas = (
        Pessoa.objects.filter(usuario__isnull=True)
        .filter(
            Q(nome__icontains=query)
            | Q(doc__icontains=query)
            | Q(email__icontains=query)
        )
        .order_by("nome")[:20]
    )  # Limita a 20 resultados

    context = {"pessoas": pessoas, "query": query}

    return render(request, "components/pessoas_autocomplete.html", context)


@login_required
@group_area_required
def buscar_pessoas_para_edicao(request, area):
    """
    API para busca de pessoas via HTMX autocomplete na edição
    Inclui a pessoa atual do usuário sendo editado
    """
    query = request.GET.get("q", "").strip()
    usuario_id = request.GET.get("usuario_id")

    if len(query) < 2:
        return render(
            request, "components/pessoas_autocomplete.html", {"pessoas": []}
        )

    # Busca pessoas sem usuário OU a pessoa atual do usuário sendo editado
    filter_condition = Q(usuario__isnull=True)
    if usuario_id:
        filter_condition |= Q(usuario__id=usuario_id)

    pessoas = (
        Pessoa.objects.filter(filter_condition)
        .filter(
            Q(nome__icontains=query)
            | Q(doc__icontains=query)
            | Q(email__icontains=query)
        )
        .order_by("nome")[:20]
    )

    context = {"pessoas": pessoas, "query": query}

    return render(request, "components/pessoas_autocomplete.html", context)
