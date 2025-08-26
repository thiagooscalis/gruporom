# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from core.models import Caravana, Bloqueio, Passageiro


@login_required
@user_passes_test(lambda u: u.groups.filter(name="Comercial").exists())
def home(request):
    """
    View principal da área comercial
    """
    context = {
        "title": "Área Comercial",
    }

    return render(request, "comercial/home.html", context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name="Comercial").exists())
def nova_venda(request):
    """
    View para página de nova venda com opções de tipos de venda
    """
    context = {
        "title": "Nova Venda",
    }

    return render(request, "comercial/nova_venda.html", context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name="Comercial").exists())
def caravanas_disponiveis(request):
    """
    View para listagem de caravanas disponíveis para venda
    """
    caravanas = (
        Caravana.objects.all()
        .select_related("empresa", "promotor", "responsavel")
        .prefetch_related("lideres")
        .order_by("data_contrato")
    )
    
    # Adicionar cálculo de disponíveis
    for caravana in caravanas:
        # Conta passageiros em todos os bloqueios desta caravana
        total_passageiros_vendidos = Passageiro.objects.filter(
            bloqueio__caravana=caravana
        ).count()
        caravana.total_passageiros_vendidos = total_passageiros_vendidos
        caravana.passageiros_disponiveis = caravana.quantidade - total_passageiros_vendidos

    context = {
        "title": "Caravanas Disponíveis",
        "caravanas": caravanas,
    }

    return render(request, "comercial/caravanas_disponiveis.html", context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name="Comercial").exists())
def caravana_detalhes(request, caravana_id):
    """
    View para detalhes da caravana selecionada para venda
    """
    caravana = get_object_or_404(Caravana, id=caravana_id)
    
    # Buscar bloqueios relacionados à caravana
    bloqueios = Bloqueio.objects.filter(caravana=caravana, ativo=True).prefetch_related(
        'paises', 'hoteis', 'inclusos'
    ).order_by('saida')
    
    # Calcular passageiros disponíveis
    total_passageiros_vendidos = Passageiro.objects.filter(
        bloqueio__caravana=caravana
    ).count()
    passageiros_disponiveis = caravana.quantidade - total_passageiros_vendidos
    
    context = {
        "title": f"Detalhes - {caravana.nome}",
        "caravana": caravana,
        "bloqueios": bloqueios,
        "passageiros_disponiveis": passageiros_disponiveis,
        "total_passageiros_vendidos": total_passageiros_vendidos,
        "quantidade_range": range(1, max(1, passageiros_disponiveis + 1)),
    }
    
    return render(request, "comercial/caravana_detalhes.html", context)
