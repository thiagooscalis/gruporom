import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from core.models import Pessoa
from core.choices import TIPO_DOC_CHOICES, SEXO_CHOICES
from core.factories import PessoaFactory, PessoaJuridicaFactory


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
            nascimento=timezone.now().date(),
            email1="joao@example.com",
            ddi1="55",
            ddd1="11",
            telefone1="999999999"
        )
        assert pessoa.id is not None
        assert pessoa.tipo_doc == "CPF"
        assert pessoa.doc == "12345678901"
        assert pessoa.nome == "João da Silva"
        # Verifica se telefone e email diretos foram criados
        assert pessoa.email1 == "joao@example.com"
        assert pessoa.telefone1 == "999999999"
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
        # Verifica se email e telefone diretos foram criados
        assert pessoa.email1 is not None
        assert pessoa.telefone1 is not None

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
        from core.factories import PaisFactory
        pais_brasil = PaisFactory(nome="Brasil", iso="BR")
        
        pessoa = PessoaFactory(
            nome="João Silva",
            passaporte_numero="AB123456",
            passaporte_validade=timezone.now().date(),
            pais=pais_brasil
        )
        assert pessoa.passaporte_numero == "AB123456"
        assert pessoa.passaporte_validade is not None
        assert pessoa.pais.nome == "Brasil"

    def test_telefone_properties(self):
        """Testa propriedades de telefone da pessoa"""
        pessoa = PessoaFactory(
            ddi1="55",
            ddd1="11", 
            telefone1="999999999"
        )
        
        assert pessoa.telefone_formatado is not None
        assert pessoa.telefone_completo == "+5511999999999"
        assert pessoa.telefone_principal is not None

    def test_email_properties(self):
        """Testa propriedades de email da pessoa"""
        pessoa = PessoaFactory(email1="test@example.com")
        
        assert pessoa.email_principal == "test@example.com"
        assert pessoa.email1 == "test@example.com"

    def test_multiplos_telefones(self):
        """Testa pessoa com múltiplos telefones"""
        pessoa = PessoaFactory(
            ddi1="55",
            ddd1="11", 
            telefone1="999999999",
            ddi2="55",
            ddd2="21",
            telefone2="888888888"
        )
        
        assert pessoa.telefone1 == "999999999"
        assert pessoa.telefone2 == "888888888"
        assert pessoa.telefone_principal is not None

    def test_multiplos_emails(self):
        """Testa pessoa com múltiplos emails"""
        pessoa = PessoaFactory(
            email1="primary@example.com",
            email2="secondary@example.com"
        )
        
        assert pessoa.email1 == "primary@example.com"
        assert pessoa.email2 == "secondary@example.com"
        assert pessoa.email_principal == "primary@example.com"

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