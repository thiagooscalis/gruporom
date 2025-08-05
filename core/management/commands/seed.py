from django.core.management.base import BaseCommand
from core.seeds.usuario import UsuarioSeeder
from core.seeds.whatsapp import seed_whatsapp


class Command(BaseCommand):
    help = 'Executa os seeders para popular o banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--seeder',
            type=str,
            help='Nome específico do seeder para executar (ex: usuario)',
        )

    def handle(self, *args, **options):
        seeder_name = options.get('seeder')
        
        if seeder_name:
            self.run_specific_seeder(seeder_name)
        else:
            self.run_all_seeders()

    def run_specific_seeder(self, seeder_name):
        """Executa um seeder específico"""
        if seeder_name.lower() == 'usuario':
            self.stdout.write(
                self.style.SUCCESS('Executando UsuarioSeeder...')
            )
            UsuarioSeeder.run()
        elif seeder_name.lower() == 'whatsapp':
            self.stdout.write(
                self.style.SUCCESS('Executando WhatsApp Seeder...')
            )
            seed_whatsapp()
        else:
            self.stdout.write(
                self.style.ERROR(f'Seeder "{seeder_name}" não encontrado.')
            )

    def run_all_seeders(self):
        """Executa todos os seeders disponíveis"""
        self.stdout.write(
            self.style.SUCCESS('Executando todos os seeders...')
        )
        
        # Lista de todos os seeders disponíveis
        seeders = [
            ('UsuarioSeeder', UsuarioSeeder),
        ]
        
        # Função seeders
        function_seeders = [
            ('WhatsApp Seeder', seed_whatsapp),
        ]
        
        for seeder_name, seeder_class in seeders:
            self.stdout.write(f'Executando {seeder_name}...')
            try:
                seeder_class.run()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {seeder_name} executado com sucesso')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Erro ao executar {seeder_name}: {str(e)}')
                )
        
        # Executa function seeders
        for seeder_name, seeder_function in function_seeders:
            self.stdout.write(f'Executando {seeder_name}...')
            try:
                seeder_function()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {seeder_name} executado com sucesso')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Erro ao executar {seeder_name}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\nTodos os seeders foram executados!')
        )