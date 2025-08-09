import pytest
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.db import IntegrityError
from core.models import Usuario, Pessoa
from core.choices import TIPO_DOC_CHOICES


@pytest.mark.django_db
class TestUsuarioModel:
    """Testes para o model Usuario"""

    @pytest.fixture
    def pessoa(self):
        """Fixture para criar uma pessoa para os testes"""
        from core.factories import PessoaFactory
        return PessoaFactory(
            tipo_doc="CPF",
            doc="12345678901",
            nome="João da Silva"
        )

    def test_create_usuario(self, pessoa):
        """Testa criação de usuário com dados válidos"""
        usuario = Usuario.objects.create_user(
            username="joao.silva",
            password="senhaSegura123",
            pessoa=pessoa
        )
        assert usuario.id is not None
        assert usuario.username == "joao.silva"
        assert usuario.pessoa == pessoa
        assert usuario.is_active is True
        assert usuario.is_staff is False
        assert usuario.is_superuser is False

    def test_create_superuser(self, pessoa):
        """Testa criação de superusuário"""
        usuario = Usuario.objects.create_superuser(
            username="admin",
            password="senhaSegura123",
            pessoa=pessoa
        )
        assert usuario.is_staff is True
        assert usuario.is_superuser is True
        assert usuario.is_active is True

    def test_username_unique(self, pessoa):
        """Testa que username deve ser único"""
        Usuario.objects.create_user(
            username="usuario1",
            password="senha123",
            pessoa=pessoa
        )
        
        # Criar nova pessoa para o segundo usuário
        from core.factories import PessoaFactory
        pessoa2 = PessoaFactory(
            tipo_doc="CPF",
            doc="98765432109",
            nome="Maria Santos"
        )
        
        with pytest.raises(IntegrityError):
            Usuario.objects.create_user(
                username="usuario1",
                password="senha123",
                pessoa=pessoa2
            )

    def test_authenticate_usuario(self, pessoa):
        """Testa autenticação de usuário"""
        usuario = Usuario.objects.create_user(
            username="joao.silva",
            password="senhaSegura123",
            pessoa=pessoa
        )
        
        # Autenticação com credenciais corretas
        authenticated = authenticate(username="joao.silva", password="senhaSegura123")
        assert authenticated == usuario
        
        # Autenticação com senha incorreta
        authenticated = authenticate(username="joao.silva", password="senhaErrada")
        assert authenticated is None
        
        # Autenticação com usuário inexistente
        authenticated = authenticate(username="naoexiste", password="senha123")
        assert authenticated is None

    def test_str_representation(self, pessoa):
        """Testa representação em string do model"""
        usuario = Usuario.objects.create_user(
            username="joao.silva",
            password="senha123",
            pessoa=pessoa
        )
        assert str(usuario) == "joao.silva"

    def test_nome_property(self, pessoa):
        """Testa propriedade nome do usuário"""
        usuario = Usuario.objects.create_user(
            username="joao.silva",
            password="senha123",
            pessoa=pessoa
        )
        assert usuario.nome == "João da Silva"

    def test_email_property(self, pessoa):
        """Testa propriedade email do usuário"""
        usuario = Usuario.objects.create_user(
            username="joao.silva",
            password="senha123",
            pessoa=pessoa
        )
        # Email agora vem do EmailFactory através da propriedade da pessoa
        assert usuario.email is not None
        assert "@" in usuario.email

    def test_usuario_groups(self, pessoa):
        """Testa associação de usuário com grupos"""
        # Criar grupo
        grupo_admin = Group.objects.create(name="Administração")
        grupo_vendas = Group.objects.create(name="Vendas")
        
        usuario = Usuario.objects.create_user(
            username="joao.silva",
            password="senha123",
            pessoa=pessoa
        )
        
        # Adicionar usuário aos grupos
        usuario.groups.add(grupo_admin, grupo_vendas)
        
        assert usuario.groups.count() == 2
        assert grupo_admin in usuario.groups.all()
        assert grupo_vendas in usuario.groups.all()

    def test_usuario_permissions(self, pessoa):
        """Testa sistema de permissões do usuário"""
        usuario = Usuario.objects.create_user(
            username="joao.silva",
            password="senha123",
            pessoa=pessoa
        )
        
        # Usuário normal não tem permissões por padrão
        assert usuario.user_permissions.count() == 0
        
        # Verificar método has_perm
        assert usuario.has_perm('core.add_pessoa') is False
        
        # Criar nova pessoa para o superusuário
        from core.factories import PessoaFactory
        pessoa_admin = PessoaFactory(
            tipo_doc="CPF",
            doc="11111111111",
            nome="Admin User"
        )
        
        # Superusuário tem todas as permissões
        superuser = Usuario.objects.create_superuser(
            username="admin",
            password="senha123",
            pessoa=pessoa_admin
        )
        assert superuser.has_perm('core.add_pessoa') is True

    def test_usuario_sem_pessoa(self):
        """Testa que usuário deve ter uma pessoa associada"""
        with pytest.raises(IntegrityError):
            Usuario.objects.create_user(
                username="usuario.sem.pessoa",
                password="senha123",
                pessoa=None
            )

    def test_usuario_password_hashing(self, pessoa):
        """Testa que senha é hasheada corretamente"""
        usuario = Usuario.objects.create_user(
            username="joao.silva",
            password="senhaSegura123",
            pessoa=pessoa
        )
        
        # Senha não deve ser armazenada em texto plano
        assert usuario.password != "senhaSegura123"
        # Em testes usa MD5 hasher para performance
        assert usuario.password.startswith(("pbkdf2_sha256$", "md5$"))
        
        # check_password deve funcionar
        assert usuario.check_password("senhaSegura123") is True
        assert usuario.check_password("senhaErrada") is False

    def test_usuario_is_active(self, pessoa):
        """Testa flag is_active do usuário"""
        usuario = Usuario.objects.create_user(
            username="joao.silva",
            password="senha123",
            pessoa=pessoa
        )
        
        assert usuario.is_active is True
        
        # Desativar usuário
        usuario.is_active = False
        usuario.save()
        
        # Usuário inativo não pode autenticar
        authenticated = authenticate(username="joao.silva", password="senha123")
        assert authenticated is None

    def test_usuario_timestamps(self, pessoa):
        """Testa campos de timestamp do usuário"""
        usuario = Usuario.objects.create_user(
            username="joao.silva",
            password="senha123",
            pessoa=pessoa
        )
        
        assert usuario.date_joined is not None
        assert usuario.last_login is None
        
        # Simular login
        usuario.last_login = usuario.date_joined
        usuario.save()
        
        assert usuario.last_login is not None