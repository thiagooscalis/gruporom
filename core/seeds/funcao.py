# -*- coding: utf-8 -*-
from django.db import transaction
from core.models import Funcao


class FuncaoSeeder:
    """
    Seeder para popular funções eclesiásticas principais
    Inclui títulos religiosos comuns e mentor(a)
    """

    @staticmethod
    def run():
        """
        Executa o seeder de funções eclesiásticas
        """
        print("⛪ Executando Funcao Seeder...")
        
        # Verificar se já existem funções
        funcoes_existentes = Funcao.objects.count()
        if funcoes_existentes > 0:
            print(f"✅ {funcoes_existentes} funções já existem no sistema!")
            return
        
        try:
            funcoes_criadas = FuncaoSeeder.criar_funcoes_eclesiasticas()
            print(f"✅ {funcoes_criadas} funções eclesiásticas cadastradas com sucesso!")
            print(f"📊 Total de funções no sistema: {Funcao.objects.count()}")
            
        except Exception as e:
            print(f"❌ Erro ao processar funções: {str(e)}")
    
    @staticmethod
    def criar_funcoes_eclesiasticas():
        """
        Cria as principais funções eclesiásticas
        """
        funcoes_data = [
            # Liderança Eclesiástica
            {
                'masculino': 'Pastor',
                'feminino': 'Pastora',
                'abreviacao_masculino': 'Pr.',
                'abreviacao_feminino': 'Pra.'
            },
            {
                'masculino': 'Reverendo',
                'feminino': 'Reverenda',
                'abreviacao_masculino': 'Rev.',
                'abreviacao_feminino': 'Rev.ª'
            },
            {
                'masculino': 'Ministro',
                'feminino': 'Ministra',
                'abreviacao_masculino': 'Min.',
                'abreviacao_feminino': 'Min.ª'
            },
            {
                'masculino': 'Padre',
                'feminino': 'Madre',
                'abreviacao_masculino': 'Pe.',
                'abreviacao_feminino': 'M.'
            },
            {
                'masculino': 'Bispo',
                'feminino': 'Bispa',
                'abreviacao_masculino': 'Bpo.',
                'abreviacao_feminino': 'Bpa.'
            },
            {
                'masculino': 'Arcebispo',
                'feminino': 'Arcebispa',
                'abreviacao_masculino': 'Arceb.',
                'abreviacao_feminino': 'Arceba.'
            },
            {
                'masculino': 'Cardeal',
                'feminino': 'Cardeal',
                'abreviacao_masculino': 'Card.',
                'abreviacao_feminino': 'Card.'
            },
            
            # Liderança de Ministérios
            {
                'masculino': 'Diácono',
                'feminino': 'Diaconisa',
                'abreviacao_masculino': 'Dc.',
                'abreviacao_feminino': 'Dca.'
            },
            {
                'masculino': 'Presbítero',
                'feminino': 'Presbítera',
                'abreviacao_masculino': 'Pb.',
                'abreviacao_feminino': 'Pba.'
            },
            {
                'masculino': 'Evangelista',
                'feminino': 'Evangelista',
                'abreviacao_masculino': 'Ev.',
                'abreviacao_feminino': 'Eva.'
            },
            {
                'masculino': 'Apóstolo',
                'feminino': 'Apóstola',
                'abreviacao_masculino': 'Ap.',
                'abreviacao_feminino': 'Apa.'
            },
            {
                'masculino': 'Profeta',
                'feminino': 'Profetisa',
                'abreviacao_masculino': 'Pf.',
                'abreviacao_feminino': 'Pfa.'
            },
            
            # Funções Educativas e de Mentoria
            {
                'masculino': 'Mentor',
                'feminino': 'Mentora',
                'abreviacao_masculino': 'Ment.',
                'abreviacao_feminino': 'Ment.ª'
            },
            {
                'masculino': 'Mestre',
                'feminino': 'Mestra',
                'abreviacao_masculino': 'Me.',
                'abreviacao_feminino': 'Ma.'
            },
            {
                'masculino': 'Doutor',
                'feminino': 'Doutora',
                'abreviacao_masculino': 'Dr.',
                'abreviacao_feminino': 'Dra.'
            },
            {
                'masculino': 'Professor',
                'feminino': 'Professora',
                'abreviacao_masculino': 'Prof.',
                'abreviacao_feminino': 'Profa.'
            },
            
            # Funções Administrativas
            {
                'masculino': 'Presidente',
                'feminino': 'Presidenta',
                'abreviacao_masculino': 'Pres.',
                'abreviacao_feminino': 'Pres.ª'
            },
            {
                'masculino': 'Diretor',
                'feminino': 'Diretora',
                'abreviacao_masculino': 'Dir.',
                'abreviacao_feminino': 'Dir.ª'
            },
            {
                'masculino': 'Coordenador',
                'feminino': 'Coordenadora',
                'abreviacao_masculino': 'Coord.',
                'abreviacao_feminino': 'Coord.ª'
            },
            
            # Funções Especiais
            {
                'masculino': 'Missionário',
                'feminino': 'Missionária',
                'abreviacao_masculino': 'Miss.',
                'abreviacao_feminino': 'Miss.ª'
            }
        ]
        
        funcoes_criadas = 0
        
        with transaction.atomic():
            for funcao_data in funcoes_data:
                try:
                    # Verificar se já existe (por masculino)
                    if not Funcao.objects.filter(masculino=funcao_data['masculino']).exists():
                        Funcao.objects.create(**funcao_data)
                        funcoes_criadas += 1
                        
                        # Feedback a cada 5 funções
                        if funcoes_criadas % 5 == 0:
                            print(f"📋 {funcoes_criadas} funções processadas...")
                
                except Exception as e:
                    print(f"⚠️  Erro ao criar função {funcao_data['masculino']}: {str(e)}")
                    continue
        
        # Estatísticas finais
        print("📊 Estatísticas do processamento:")
        print(f"   ✅ Funções criadas: {funcoes_criadas}")
        print(f"   📈 Total no sistema: {Funcao.objects.count()}")
        
        # Destacar algumas funções importantes
        if funcoes_criadas > 0:
            print("⛪ Funções eclesiásticas principais disponíveis:")
            print("   🙏 Pastor/Pastora, Reverendo/Reverenda")
            print("   👨‍🏫 Mentor/Mentora, Professor/Professora") 
            print("   👔 Presidente/Presidenta, Diretor/Diretora")
        
        return funcoes_criadas