from django.contrib.auth.models import Group
from core.models import Usuario, Pessoa
from core.choices import TIPO_DOC_CHOICES


class UsuarioSeeder:
    """
    Seeder para criar usuário administrador padrão
    """
    
    @staticmethod
    def create_admin_user():
        """
        Cria um usuário administrador padrão se não existir
        """
        # Verifica se já existe um usuário thiago
        if Usuario.objects.filter(username='thiago').exists():
            print("Usuário thiago já existe.")
            return
        
        # Cria ou obtém o grupo de administração
        admin_group, created = Group.objects.get_or_create(name='Administração')
        if created:
            print("Grupo 'Administração' criado.")
        
        # Cria a pessoa do administrador
        admin_pessoa = Pessoa.objects.create(
            nome="Thiago Martins",
            doc="12345678901",  # CPF somente números
            tipo_doc="CPF",
            email="thiago@gruporom.com.br",
            telefone="11999999999"  # Telefone somente números
        )
        
        # Cria o usuário administrador
        admin_user = Usuario.objects.create_superuser(
            username='thiago',
            password='admin123',
            pessoa=admin_pessoa
        )
        
        # Adiciona ao grupo de administração
        admin_user.groups.add(admin_group)
        
        print(f"Usuário administrador criado:")
        print(f"Username: thiago")
        print(f"Password: admin123")
        print(f"Email: {admin_pessoa.email}")
        
        return admin_user
    
    @staticmethod
    def run():
        """
        Executa o seeder
        """
        print("Executando UsuarioSeeder...")
        UsuarioSeeder.create_admin_user()
        print("UsuarioSeeder concluído.")