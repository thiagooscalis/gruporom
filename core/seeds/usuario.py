from django.contrib.auth.models import Group
from core.models import Usuario, Pessoa
from core.choices import TIPO_DOC_CHOICES, TIPO_EMPRESA_CHOICES


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

        promotor_group, created = Group.objects.get_or_create(
            name="Promotor"
        )
        if created:
            print("Grupo 'Promotor' criado.")

        # Verifica se já existe um usuário thiago
        if Usuario.objects.filter(username="thiago").exists():
            print("Usuário thiago já existe.")
            # Atualiza os grupos do usuário admin existente
            admin_user = Usuario.objects.get(username="thiago")
            admin_user.groups.add(
                admin_group, comercial_group, operacional_group
            )
            
            # Verifica se já tem empresas associadas
            if not admin_user.empresas.exists():
                # Cria empresas do Grupo ROM se não existirem
                empresas = []
                for tipo_empresa, _ in TIPO_EMPRESA_CHOICES:
                    # Verifica se empresa já existe
                    empresa = Pessoa.objects.filter(
                        nome=f"ROM {tipo_empresa}",
                        empresa_gruporom=True
                    ).first()
                    
                    if not empresa:
                        empresa = Pessoa.objects.create(
                            nome=f"ROM {tipo_empresa}",
                            doc=f"12345678{len(empresas):03d}001",
                            tipo_doc="CNPJ",
                            email=f"contato@rom{tipo_empresa.lower().replace(' ', '')}.com.br",
                            telefone="11888888888",
                            empresa_gruporom=True,
                            tipo_empresa=tipo_empresa
                        )
                        print(f"Empresa criada: {empresa.nome}")
                    
                    empresas.append(empresa)
                    admin_user.empresas.add(empresa)
                
                print(f"Empresas associadas: {', '.join([e.nome for e in empresas])}")
            
            print("Grupos e empresas atualizados para o usuário thiago.")
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
        
        # Cria empresas do Grupo ROM para cada tipo
        empresas = []
        for tipo_empresa, _ in TIPO_EMPRESA_CHOICES:
            empresa = Pessoa.objects.create(
                nome=f"ROM {tipo_empresa}",
                doc=f"12345678{len(empresas):03d}001",  # CNPJ sequencial
                tipo_doc="CNPJ",
                email=f"contato@rom{tipo_empresa.lower().replace(' ', '')}.com.br",
                telefone="11888888888",
                empresa_gruporom=True,
                tipo_empresa=tipo_empresa
            )
            empresas.append(empresa)
            admin_user.empresas.add(empresa)
            print(f"Empresa criada: {empresa.nome}")

        print(f"Usuário administrador criado:")
        print(f"Username: thiago")
        print(f"Password: admin123")
        print(f"Email: {admin_pessoa.email}")
        print(f"Grupos: Administração, Comercial, Operacional")
        print(f"Empresas: {', '.join([e.nome for e in empresas])}")

        return admin_user

    @staticmethod
    def run():
        """
        Executa o seeder
        """
        print("Executando UsuarioSeeder...")
        UsuarioSeeder.create_admin_user()
        print("UsuarioSeeder concluído.")
