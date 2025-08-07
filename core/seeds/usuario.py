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
        # Cria ou obtém os grupos necessários
        admin_group, created = Group.objects.get_or_create(
            name="Administração"
        )
        if created:
            print("Grupo 'Administração' criado.")

        comercial_group, created = Group.objects.get_or_create(
            name="Comercial"
        )
        if created:
            print("Grupo 'Comercial' criado.")

        operacional_group, created = Group.objects.get_or_create(
            name="Operacional"
        )
        if created:
            print("Grupo 'Operacional' criado.")

        # Verifica se já existe um usuário thiago
        if Usuario.objects.filter(username="thiago").exists():
            print("Usuário thiago já existe.")
            # Atualiza os grupos do usuário admin existente
            admin_user = Usuario.objects.get(username="thiago")
            admin_user.groups.add(
                admin_group, comercial_group, operacional_group
            )
            print("Grupos atualizados para o usuário thiago.")
            return admin_user

        # Cria a pessoa do administrador
        admin_pessoa = Pessoa.objects.create(
            nome="Thiago Martins",
            doc="12345678901",  # CPF somente números
            tipo_doc="CPF",
            email="thiago@gruporom.com.br",
            telefone="11999999999",  # Telefone somente números
        )

        # Cria o usuário administrador
        admin_user = Usuario.objects.create_superuser(
            username="thiago", password="admin123", pessoa=admin_pessoa
        )

        # Adiciona aos grupos
        admin_user.groups.add(admin_group, comercial_group, operacional_group)

        print(f"Usuário administrador criado:")
        print(f"Username: thiago")
        print(f"Password: admin123")
        print(f"Email: {admin_pessoa.email}")
        print(f"Grupos: Administração, Comercial, Operacional")

        return admin_user

    @staticmethod
    def run():
        """
        Executa o seeder
        """
        print("Executando UsuarioSeeder...")
        UsuarioSeeder.create_admin_user()
        print("UsuarioSeeder concluído.")
