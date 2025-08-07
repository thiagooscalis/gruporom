# -*- coding: utf-8 -*-
import json
import os
from core.models import Pais

def seed():
    """
    Popula a tabela de países com dados do arquivo JSON
    """
    print("🌍 Populando países...")
    
    # Caminho para o arquivo JSON
    arquivo_paises = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'data', 
        'paises.json'
    )
    
    try:
        with open(arquivo_paises, 'r', encoding='utf-8') as f:
            paises_data = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo paises.json não encontrado!")
        return
    
    # Obter ISOs existentes em uma única consulta
    isos_existentes = set(Pais.objects.values_list('iso', flat=True))
    
    paises_para_criar = []
    paises_criados = 0
    
    # Preparar países para criação em massa
    for pais_data in paises_data:
        if pais_data['iso'] not in isos_existentes:
            paises_para_criar.append(
                Pais(
                    iso=pais_data['iso'],
                    nome=pais_data['nome']
                )
            )
    
    # Criar países em massa se houver novos
    if paises_para_criar:
        Pais.objects.bulk_create(paises_para_criar)
        paises_criados = len(paises_para_criar)
    
    print(f"✅ {paises_criados} países criados!")
    print(f"📊 Total de países no sistema: {Pais.objects.count()}")