import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from core.models import Pessoa
from core.choices import TIPO_DOC_CHOICES, SEXO_CHOICES


@pytest.mark.django_db
class TestPessoaModel:
    """Testes para o model Pessoa"""

    def test_create_pessoa_fisica(self):
        """Testa criação de pessoa física com dados válidos"""
        pessoa = Pessoa.objects.create(
            tipo_doc="CPF",
            doc="12345678901",
            nome="João da Silva",
            sexo="Masculino",
            nascimento=timezone.now().date(),
            email="joao@example.com",
            telefone="11999999999"
        )
        assert pessoa.id is not None
        assert pessoa.tipo_doc == "CPF"
        assert pessoa.doc == "12345678901"
        assert pessoa.nome == "João da Silva"

    def test_create_pessoa_juridica(self):
        """Testa criação de pessoa jurídica com dados válidos"""
        pessoa = Pessoa.objects.create(
            tipo_doc="CNPJ",
            doc="12345678000199",
            nome="Empresa ABC Ltda",
            email="contato@empresa.com",
            telefone="1133333333"
        )
        assert pessoa.id is not None
        assert pessoa.tipo_doc == "CNPJ"
        assert pessoa.doc == "12345678000199"
        assert pessoa.sexo is None
        assert pessoa.nascimento is None

    def test_doc_unique(self):
        """Testa que doc deve ser único"""
        Pessoa.objects.create(
            tipo_doc="CPF",
            doc="12345678901",
            nome="Pessoa 1",
            email="pessoa1@example.com"
        )
        
        with pytest.raises(IntegrityError):
            Pessoa.objects.create(
                tipo_doc="CPF",
                doc="12345678901",
                nome="Pessoa 2",
                email="pessoa2@example.com"
            )

    def test_str_representation(self):
        """Testa representação em string do model"""
        pessoa = Pessoa.objects.create(
            tipo_doc="CPF",
            doc="12345678901",
            nome="João da Silva",
            email="joao@example.com"
        )
        assert str(pessoa) == "João da Silva"

    def test_pessoa_com_endereco_completo(self):
        """Testa criação de pessoa com endereço completo"""
        pessoa = Pessoa.objects.create(
            tipo_doc="CPF",
            doc="12345678901",
            nome="Maria Santos",
            email="maria@example.com",
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
        pessoa = Pessoa.objects.create(
            tipo_doc="CPF",
            doc="12345678901",
            nome="João Silva",
            email="joao@example.com",
            passaporte_numero="AB123456",
            passaporte_validade=timezone.now().date(),
            pais="Brasil"
        )
        assert pessoa.passaporte_numero == "AB123456"
        assert pessoa.passaporte_validade is not None
        assert pessoa.pais == "Brasil"

    def test_blank_fields(self):
        """Testa que campos opcionais podem ser deixados em branco"""
        pessoa = Pessoa.objects.create(
            tipo_doc="CPF",
            doc="12345678901",
            nome="João",
            email="joao@example.com"
        )
        assert pessoa.telefone == ""
        assert pessoa.cep is None
        assert pessoa.endereco is None
        assert pessoa.numero is None
        assert pessoa.complemento is None
        assert pessoa.bairro is None
        assert pessoa.cidade is None
        assert pessoa.estado is None
        assert pessoa.pais is None

    def test_max_length_fields(self):
        """Testa comprimento máximo dos campos"""
        pessoa = Pessoa(
            tipo_doc="CPF",
            doc="12345678901",
            nome="N" * 255,  # 255 caracteres
            email="email@example.com",
            telefone="11999999999"  # Campo obrigatório
        )
        pessoa.full_clean()  # Não deve lançar exceção
        
        # Testando campo com mais que o máximo
        pessoa.nome = "N" * 256  # 256 caracteres
        with pytest.raises(ValidationError):
            pessoa.full_clean()

    def test_tipo_pessoa_property(self):
        """Testa a propriedade tipo_pessoa"""
        # Pessoa física
        pessoa_fisica = Pessoa.objects.create(
            tipo_doc="CPF",
            doc="12345678901",
            nome="João",
            email="joao@example.com"
        )
        assert pessoa_fisica.tipo_pessoa == "FISICA"
        assert pessoa_fisica.get_tipo_pessoa_display() == "Pessoa Física"
        
        # Pessoa jurídica
        pessoa_juridica = Pessoa.objects.create(
            tipo_doc="CNPJ",
            doc="12345678000199",
            nome="Empresa ABC",
            email="empresa@example.com"
        )
        assert pessoa_juridica.tipo_pessoa == "JURIDICA"
        assert pessoa_juridica.get_tipo_pessoa_display() == "Pessoa Jurídica"
        
        # Passaporte (assume física)
        pessoa_passaporte = Pessoa.objects.create(
            tipo_doc="Passaporte",
            doc="AB123456",
            nome="John Doe",
            email="john@example.com"
        )
        assert pessoa_passaporte.tipo_pessoa == "FISICA"

    def test_slug_generation(self):
        """Testa geração automática de slug"""
        pessoa = Pessoa.objects.create(
            tipo_doc="CPF",
            doc="12345678901",
            nome="João da Silva",
            email="joao@example.com"
        )
        pessoa.save()  # Slug deve ser gerado no save
        assert pessoa.slug is not None  # O slug será gerado no save pelo model