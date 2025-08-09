import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from core.models import Pessoa, Telefone, Email
from core.choices import TIPO_DOC_CHOICES, SEXO_CHOICES
from core.factories import PessoaFactory, PessoaJuridicaFactory, TelefoneFactory, EmailFactory


@pytest.mark.django_db
class TestPessoaModel:
    """Testes para o model Pessoa"""

    def test_create_pessoa_fisica(self):
        """Testa criação de pessoa física com dados válidos"""
        pessoa = PessoaFactory(
            tipo_doc="CPF",
            doc="12345678901",
            nome="João da Silva",
            sexo="Masculino",
            nascimento=timezone.now().date()
        )
        assert pessoa.id is not None
        assert pessoa.tipo_doc == "CPF"
        assert pessoa.doc == "12345678901"
        assert pessoa.nome == "João da Silva"
        # Verifica se telefone e email foram criados
        assert pessoa.telefone_principal is not None
        assert pessoa.email_principal is not None

    def test_create_pessoa_juridica(self):
        """Testa criação de pessoa jurídica com dados válidos"""
        pessoa = PessoaJuridicaFactory(
            doc="12345678000199",
            nome="Empresa ABC Ltda"
        )
        assert pessoa.id is not None
        assert pessoa.tipo_doc == "CNPJ"
        assert pessoa.doc == "12345678000199"
        assert pessoa.sexo is None
        assert pessoa.nascimento is None
        # Verifica se telefone e email foram criados
        assert pessoa.telefone_principal is not None
        assert pessoa.email_principal is not None

    def test_doc_unique(self):
        """Testa que doc deve ser único"""
        PessoaFactory(doc="12345678901", nome="Pessoa 1")
        
        with pytest.raises(IntegrityError):
            PessoaFactory(doc="12345678901", nome="Pessoa 2")

    def test_str_representation(self):
        """Testa representação em string do model"""
        pessoa = PessoaFactory(nome="João da Silva")
        assert str(pessoa) == "João da Silva"

    def test_pessoa_com_endereco_completo(self):
        """Testa criação de pessoa com endereço completo"""
        pessoa = PessoaFactory(
            nome="Maria Santos",
            cep="01310100",
            endereco="Avenida Paulista",
            numero="1578",
            complemento="Sala 20",
            bairro="Bela Vista",
            cidade="São Paulo",
            estado="SP"
        )
        assert pessoa.cep == "01310100"
        assert pessoa.endereco == "Avenida Paulista"
        assert pessoa.numero == "1578"
        assert pessoa.complemento == "Sala 20"
        assert pessoa.bairro == "Bela Vista"
        assert pessoa.cidade == "São Paulo"
        assert pessoa.estado == "SP"

    def test_pessoa_com_passaporte(self):
        """Testa criação de pessoa com dados de passaporte"""
        pessoa = PessoaFactory(
            nome="João Silva",
            passaporte_numero="AB123456",
            passaporte_validade=timezone.now().date(),
            pais="Brasil"
        )
        assert pessoa.passaporte_numero == "AB123456"
        assert pessoa.passaporte_validade is not None
        assert pessoa.pais == "Brasil"

    def test_telefone_properties(self):
        """Testa propriedades de telefone da pessoa"""
        pessoa = PessoaFactory()
        telefone = pessoa.telefone_principal
        
        assert telefone is not None
        assert telefone.principal is True
        assert pessoa.telefone_formatado is not None
        assert pessoa.telefone_completo is not None

    def test_email_properties(self):
        """Testa propriedades de email da pessoa"""
        pessoa = PessoaFactory()
        email = pessoa.email_principal
        
        assert email is not None
        assert email.principal is True
        assert pessoa.email_str is not None

    def test_multiplos_telefones(self):
        """Testa pessoa com múltiplos telefones"""
        pessoa = PessoaFactory()
        
        # Cria telefone secundário
        TelefoneFactory(pessoa=pessoa, tipo='residencial', principal=False)
        
        assert pessoa.telefones.count() == 2
        assert pessoa.telefone_principal.principal is True

    def test_multiplos_emails(self):
        """Testa pessoa com múltiplos emails"""
        pessoa = PessoaFactory()
        
        # Cria email secundário
        EmailFactory(pessoa=pessoa, tipo='profissional', principal=False)
        
        assert pessoa.emails.count() == 2
        assert pessoa.email_principal.principal is True

    def test_tipo_pessoa_property(self):
        """Testa propriedade tipo_pessoa"""
        pessoa_fisica = PessoaFactory(tipo_doc="CPF")
        assert pessoa_fisica.tipo_pessoa == "FISICA"
        
        pessoa_juridica = PessoaJuridicaFactory()
        assert pessoa_juridica.tipo_pessoa == "JURIDICA"

    def test_slug_generation(self):
        """Testa geração automática de slug"""
        pessoa = PessoaFactory(nome="João da Silva")
        assert pessoa.slug == "joao-da-silva"