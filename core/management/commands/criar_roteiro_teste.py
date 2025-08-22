#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Management command para criar roteiro de teste para um bloqueio
Roteiro: São Paulo -> Egito -> Israel -> São Paulo

Uso: python manage.py criar_roteiro_teste [--bloqueio_id=1]
"""

from django.core.management.base import BaseCommand
from core.models import Bloqueio, DiaRoteiro


class Command(BaseCommand):
    help = 'Cria um roteiro de teste para um bloqueio (Egito e Israel)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--bloqueio_id',
            type=int,
            default=1,
            help='ID do bloqueio para adicionar o roteiro'
        )
    
    def handle(self, *args, **options):
        bloqueio_id = options['bloqueio_id']
        
        try:
            bloqueio = Bloqueio.objects.get(pk=bloqueio_id)
            self.stdout.write(f"Trabalhando com bloqueio: {bloqueio}")
            
            # Limpar roteiro existente se houver
            deleted = DiaRoteiro.objects.filter(bloqueio=bloqueio).delete()
            if deleted[0] > 0:
                self.stdout.write(self.style.WARNING(f"Removidos {deleted[0]} dias de roteiro anterior."))
            
            # Criar o roteiro detalhado
            roteiros = [
                {
                    'ordem': 1,
                    'titulo': 'Saída de São Paulo',
                    'descricao': 'Encontro no Aeroporto Internacional de Guarulhos às 19h. Check-in e embarque com destino ao Cairo, Egito. Voo noturno com conexão.'
                },
                {
                    'ordem': 2,
                    'titulo': 'Chegada ao Cairo',
                    'descricao': 'Chegada ao Aeroporto Internacional do Cairo. Recepção, traslado e acomodação no hotel. Tarde livre para descanso. À noite, jantar de boas-vindas com pratos típicos egípcios.'
                },
                {
                    'ordem': 3,
                    'titulo': 'Pirâmides de Gizé e Museu Egípcio',
                    'descricao': 'Café da manhã no hotel. Visita às Pirâmides de Gizé (Quéops, Quéfren e Miquerinos), a Esfinge e o Templo do Vale. Almoço em restaurante local. À tarde, visita ao Museu Egípcio do Cairo com seu impressionante acervo, incluindo tesouros de Tutancâmon. Retorno ao hotel.'
                },
                {
                    'ordem': 4,
                    'titulo': 'Cairo - Monte Sinai',
                    'descricao': 'Saída bem cedo do hotel. Viagem através do Deserto do Sinai até o Monastério de Santa Catarina. Chegada no final da tarde. Jantar e preparação para a subida do Monte Sinai durante a madrugada.'
                },
                {
                    'ordem': 5,
                    'titulo': 'Monte Sinai - Eilat - Jerusalém',
                    'descricao': 'Madrugada: Subida ao Monte Sinai para contemplar o nascer do sol no local onde Moisés recebeu as Tábuas da Lei. Descida e visita ao Monastério de Santa Catarina. Viagem até a fronteira de Taba. Travessia para Israel por Eilat. Continuação até Jerusalém. Check-in no hotel.'
                },
                {
                    'ordem': 6,
                    'titulo': 'Jerusalém - Cidade Antiga',
                    'descricao': 'Visita à Cidade Antiga de Jerusalém: Muro das Lamentações, Via Dolorosa, Igreja do Santo Sepulcro, Monte das Oliveiras com vista panorâmica, Jardim de Getsêmani e Igreja de Todas as Nações. Almoço em restaurante árabe no Quarteirão Cristão.'
                },
                {
                    'ordem': 7,
                    'titulo': 'Belém e Mar Morto',
                    'descricao': 'Saída para Belém. Visita à Basílica da Natividade, Gruta do Nascimento de Jesus, Campo dos Pastores e Igreja de Santa Catarina. Continuação até o Mar Morto. Experiência única de flutuar nas águas salgadas. Almoço e tempo para banho. Retorno a Jerusalém.'
                },
                {
                    'ordem': 8,
                    'titulo': 'Galileia e Nazaré',
                    'descricao': 'Viagem para o norte de Israel. Visita a Nazaré: Basílica da Anunciação e Igreja de São José. Continuação para o Mar da Galileia: Cafarnaum (cidade de Pedro), Monte das Bem-Aventuranças, Tabgha (multiplicação dos pães). Passeio de barco pelo Mar da Galileia. Pernoite em Tiberíades.'
                },
                {
                    'ordem': 9,
                    'titulo': 'Galileia - Tel Aviv',
                    'descricao': 'Visita ao Rio Jordão com possibilidade de renovação das promessas do batismo. Viagem para a costa mediterrânea. Parada em Cesareia Marítima (cidade de Herodes). Chegada a Tel Aviv. City tour por Jaffa (antiga Jope), porto de onde Jonas embarcou. Tempo livre na praia. Traslado ao aeroporto.'
                },
                {
                    'ordem': 10,
                    'titulo': 'Retorno ao Brasil',
                    'descricao': 'Embarque no Aeroporto Ben Gurion de Tel Aviv com destino a São Paulo. Voo com conexão. Chegada prevista ao Aeroporto de Guarulhos no período da tarde/noite. Fim dos nossos serviços.'
                }
            ]
            
            # Criar os registros
            for roteiro_data in roteiros:
                dia = DiaRoteiro.objects.create(
                    bloqueio=bloqueio,
                    ordem=roteiro_data['ordem'],
                    titulo=roteiro_data['titulo'],
                    descricao=roteiro_data['descricao']
                )
                self.stdout.write(f"Criado: Dia {dia.ordem} - {dia.titulo}")
            
            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Roteiro criado com sucesso! Total de {len(roteiros)} dias."
            ))
            self.stdout.write(f"Bloqueio: {bloqueio.caravana.nome} - {bloqueio.descricao}")
            self.stdout.write(f"Data de saída: {bloqueio.saida}")
            
        except Bloqueio.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f"❌ Bloqueio com ID {bloqueio_id} não encontrado!"
            ))
            self.stdout.write("Certifique-se de que existe um bloqueio cadastrado no sistema.")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao criar roteiro: {e}"))