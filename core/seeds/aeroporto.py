# -*- coding: utf-8 -*-
import json
import os
from django.db import transaction
from django.conf import settings
from core.models import Aeroporto, Cidade, Pais


class AeroportoSeeder:
    """
    Seeder para popular aeroportos a partir do arquivo JSON
    Cadastra apenas aeroportos com todos os campos válidos
    """

    @staticmethod
    def run():
        """
        Executa o seeder de aeroportos
        """
        print("🛫 Executando Aeroporto Seeder...")
        
        # Caminho para o arquivo JSON
        json_path = os.path.join(settings.BASE_DIR, 'json', 'aeroportos.json')
        
        if not os.path.exists(json_path):
            print("❌ Arquivo aeroportos.json não encontrado em json/aeroportos.json")
            return
        
        # Verificar se já existem aeroportos
        aeroportos_existentes = Aeroporto.objects.count()
        if aeroportos_existentes > 0:
            print(f"✅ {aeroportos_existentes} aeroportos já existem no sistema!")
            return
        
        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                aeroportos_data = json.load(file)
            
            print(f"📄 Arquivo carregado com {len(aeroportos_data)} registros")
            
            # Processar aeroportos
            aeroportos_criados = AeroportoSeeder.processar_aeroportos(aeroportos_data)
            
            print(f"✅ {aeroportos_criados} aeroportos cadastrados com sucesso!")
            print(f"📊 Total de aeroportos no sistema: {Aeroporto.objects.count()}")
            
        except Exception as e:
            print(f"❌ Erro ao processar aeroportos: {str(e)}")
    
    @staticmethod
    def processar_aeroportos(aeroportos_data):
        """
        Processa os dados dos aeroportos e cadastra os válidos
        """
        aeroportos_criados = 0
        aeroportos_ignorados = 0
        paises_nao_encontrados = set()
        cidades_criadas = 0
        
        # Cache de países e cidades para performance
        paises_cache = {pais.iso: pais for pais in Pais.objects.all()}
        cidades_cache = {}
        
        with transaction.atomic():
            for aeroporto_data in aeroportos_data:
                try:
                    # Validar se todos os campos obrigatórios estão presentes e válidos
                    if not AeroportoSeeder.validar_dados_aeroporto(aeroporto_data):
                        aeroportos_ignorados += 1
                        continue
                    
                    # Extrair dados
                    nome = aeroporto_data['nome'].strip()
                    iata = aeroporto_data['iata'].strip()
                    pais_iso = aeroporto_data['pais'].strip()
                    cidade_nome = aeroporto_data['cidade'].strip()
                    timezone = aeroporto_data['tz'].strip()
                    
                    # Verificar se o país existe
                    if pais_iso not in paises_cache:
                        paises_nao_encontrados.add(pais_iso)
                        aeroportos_ignorados += 1
                        continue
                    
                    pais = paises_cache[pais_iso]
                    
                    # Criar ou obter cidade
                    cidade_key = f"{cidade_nome}_{pais.id}"
                    if cidade_key not in cidades_cache:
                        cidade, created = Cidade.objects.get_or_create(
                            nome=cidade_nome,
                            pais=pais,
                            defaults={
                                'nome': cidade_nome,
                                'pais': pais
                            }
                        )
                        cidades_cache[cidade_key] = cidade
                        if created:
                            cidades_criadas += 1
                    else:
                        cidade = cidades_cache[cidade_key]
                    
                    # Verificar se aeroporto já existe (por IATA)
                    if Aeroporto.objects.filter(iata=iata).exists():
                        aeroportos_ignorados += 1
                        continue
                    
                    # Criar aeroporto
                    Aeroporto.objects.create(
                        nome=nome,
                        iata=iata,
                        cidade=cidade,
                        timezone=timezone
                    )
                    
                    aeroportos_criados += 1
                    
                    # Feedback a cada 1000 aeroportos
                    if aeroportos_criados % 1000 == 0:
                        print(f"📍 {aeroportos_criados} aeroportos processados...")
                
                except Exception as e:
                    print(f"⚠️  Erro ao processar aeroporto {aeroporto_data.get('nome', 'UNKNOWN')}: {str(e)}")
                    aeroportos_ignorados += 1
                    continue
        
        # Estatísticas finais
        print(f"📊 Estatísticas do processamento:")
        print(f"   ✅ Aeroportos criados: {aeroportos_criados}")
        print(f"   🏙️  Cidades criadas: {cidades_criadas}")
        print(f"   ⏭️  Aeroportos ignorados: {aeroportos_ignorados}")
        
        if paises_nao_encontrados:
            print(f"   ❌ Países não encontrados: {', '.join(sorted(paises_nao_encontrados))}")
        
        return aeroportos_criados
    
    @staticmethod
    def validar_dados_aeroporto(aeroporto_data):
        """
        Valida se os dados do aeroporto estão completos e corretos
        """
        campos_obrigatorios = ['nome', 'iata', 'pais', 'cidade', 'tz']
        
        # Verificar se todos os campos existem
        for campo in campos_obrigatorios:
            if campo not in aeroporto_data:
                return False
            
            valor = aeroporto_data[campo]
            
            # Verificar se o valor não está vazio ou nulo
            if not valor or str(valor).strip() == '':
                return False
        
        # Validações específicas
        iata = str(aeroporto_data['iata']).strip()
        
        # IATA deve ter exatamente 3 caracteres e não ser "0" ou "000"
        if len(iata) != 3 or iata in ['0', '000', '   ']:
            return False
        
        # IATA deve conter apenas letras e números
        if not iata.isalnum():
            return False
        
        # País deve ter exatamente 2 caracteres (ISO-2)
        pais = str(aeroporto_data['pais']).strip()
        if len(pais) != 2 or not pais.isalpha():
            return False
        
        # Nome não pode ser muito curto
        nome = str(aeroporto_data['nome']).strip()
        if len(nome) < 3:
            return False
        
        # Cidade não pode ser muito curta
        cidade = str(aeroporto_data['cidade']).strip()
        if len(cidade) < 2:
            return False
        
        # Timezone deve ter formato válido
        timezone = str(aeroporto_data['tz']).strip()
        if '/' not in timezone or len(timezone) < 5:
            return False
        
        return True