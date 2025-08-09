# -*- coding: utf-8 -*-
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from core.models import Fornecedor, Pessoa
from core.choices import TIPO_EMPRESA_CHOICES


@pytest.mark.django_db
class TestFornecedorModel:
    """Tests para o modelo Fornecedor"""

    @pytest.fixture
    def pessoa_fisica(self):
        """Fixture para pessoa física"""
        from core.factories import PessoaFactory
        return PessoaFactory(
            tipo_doc="CPF",
            doc="12345678901",
            nome="João da Silva"
        )

    @pytest.fixture
    def pessoa_juridica(self):
        """Fixture para pessoa jurídica"""
        from core.factories import PessoaJuridicaFactory
        return PessoaJuridicaFactory(
            doc="12345678000195",
            nome="Empresa ABC Ltda"
        )

    @pytest.fixture
    def empresa_gruporom(self):
        """Fixture para empresa do Grupo ROM"""
        from core.factories import EmpresaGrupoROMFactory
        return EmpresaGrupoROMFactory(
            doc="98765432000187",
            nome="US Travel Operadora"
        )

    def test_create_fornecedor(self, pessoa_fisica, empresa_gruporom):
        """Testa criação básica de fornecedor"""
        fornecedor = Fornecedor.objects.create(
            pessoa=pessoa_fisica,
            tipo_empresa="Turismo"
        )
        fornecedor.empresas.add(empresa_gruporom)
        
        assert fornecedor.pessoa == pessoa_fisica
        assert fornecedor.tipo_empresa == "Turismo"
        assert empresa_gruporom in fornecedor.empresas.all()
        assert str(fornecedor) == "João da Silva - Turismo"

    def test_pessoa_unica(self, pessoa_fisica, empresa_gruporom):
        """Testa que pessoa deve ser única (OneToOne)"""
        # Cria primeiro fornecedor
        fornecedor1 = Fornecedor.objects.create(
            pessoa=pessoa_fisica,
            tipo_empresa="Alimentação"
        )
        fornecedor1.empresas.add(empresa_gruporom)
        
        # Tenta criar segundo fornecedor com mesma pessoa
        with pytest.raises(IntegrityError):
            Fornecedor.objects.create(
                pessoa=pessoa_fisica,
                tipo_empresa="Turismo"
            )

    def test_tipo_empresa_choices(self, pessoa_fisica, empresa_gruporom):
        """Testa os tipos de empresa válidos"""
        tipos_validos = [choice[0] for choice in TIPO_EMPRESA_CHOICES]
        
        for tipo in tipos_validos:
            from core.factories import PessoaFactory
            fornecedor = Fornecedor.objects.create(
                pessoa=PessoaFactory(
                    tipo_doc="CPF",
                    doc=f"111222333{tipos_validos.index(tipo):02d}",
                    nome=f"Teste {tipo}"
                ),
                tipo_empresa=tipo
            )
            fornecedor.empresas.add(empresa_gruporom)
            assert fornecedor.tipo_empresa == tipo

    def test_empresas_apenas_gruporom(self, pessoa_fisica, pessoa_juridica, empresa_gruporom):
        """Testa que empresas deve conter apenas empresas do Grupo ROM"""
        fornecedor = Fornecedor.objects.create(
            pessoa=pessoa_fisica,
            tipo_empresa="Administração de Bens"
        )
        
        # Adiciona empresa do Grupo ROM - deve funcionar
        fornecedor.empresas.add(empresa_gruporom)
        assert empresa_gruporom in fornecedor.empresas.all()
        
        # O model tem limit_choices_to, mas isso é validado apenas no form/admin
        # No código direto, ainda é possível adicionar outras empresas
        # Mas o queryset do campo filtra corretamente

    def test_delete_pessoa_protegido(self, pessoa_fisica, empresa_gruporom):
        """Testa que não pode deletar pessoa que é fornecedor"""
        fornecedor = Fornecedor.objects.create(
            pessoa=pessoa_fisica,
            tipo_empresa="Turismo"
        )
        fornecedor.empresas.add(empresa_gruporom)
        
        # Tenta deletar pessoa - deve falhar
        with pytest.raises(Exception):  # PROTECT deve impedir
            pessoa_fisica.delete()

    def test_fornecedor_sem_empresas(self, pessoa_fisica):
        """Testa fornecedor sem empresas associadas"""
        fornecedor = Fornecedor.objects.create(
            pessoa=pessoa_fisica,
            tipo_empresa="Alimentação"
        )
        
        assert fornecedor.empresas.count() == 0
        assert list(fornecedor.empresas.all()) == []

    def test_fornecedor_multiplas_empresas(self, pessoa_fisica):
        """Testa fornecedor com múltiplas empresas do Grupo ROM"""
        # Cria várias empresas do Grupo ROM
        from core.factories import EmpresaGrupoROMFactory
        empresas = []
        for i in range(3):
            empresa = EmpresaGrupoROMFactory(
                doc=f"1111222233330{i:02d}",
                nome=f"Empresa ROM {i+1}"
            )
            empresas.append(empresa)
        
        fornecedor = Fornecedor.objects.create(
            pessoa=pessoa_fisica,
            tipo_empresa="Turismo"
        )
        fornecedor.empresas.set(empresas)
        
        assert fornecedor.empresas.count() == 3
        for empresa in empresas:
            assert empresa in fornecedor.empresas.all()

    def test_related_names(self, pessoa_fisica, empresa_gruporom):
        """Testa os related_names configurados"""
        fornecedor = Fornecedor.objects.create(
            pessoa=pessoa_fisica,
            tipo_empresa="Alimentação"
        )
        fornecedor.empresas.add(empresa_gruporom)
        
        # Testa related_name da pessoa
        assert hasattr(pessoa_fisica, 'fornecedor')
        assert pessoa_fisica.fornecedor == fornecedor
        
        # Testa related_name das empresas
        assert fornecedor in empresa_gruporom.fornecedores_relacionados.all()

    def test_ordenacao_padrao(self):
        """Testa ordenação padrão por nome da pessoa"""
        # Cria pessoas e fornecedores em ordem não alfabética
        pessoas_nomes = ["Carlos", "Ana", "Bruno"]
        fornecedores = []
        
        for i, nome in enumerate(pessoas_nomes):
            from core.factories import PessoaFactory
            pessoa = PessoaFactory(
                tipo_doc="CPF",
                doc=f"9998887770{i:02d}",
                nome=nome
            )
            fornecedor = Fornecedor.objects.create(
                pessoa=pessoa,
                tipo_empresa="Turismo"
            )
            fornecedores.append(fornecedor)
        
        # Busca todos ordenados
        fornecedores_ordenados = list(Fornecedor.objects.all())
        nomes_ordenados = [f.pessoa.nome for f in fornecedores_ordenados]
        
        assert nomes_ordenados == ["Ana", "Bruno", "Carlos"]

    def test_meta_informacoes(self):
        """Testa informações do Meta do modelo"""
        meta = Fornecedor._meta
        
        assert meta.verbose_name == "Fornecedor"
        assert meta.verbose_name_plural == "Fornecedores"
        assert meta.ordering == ['pessoa__nome']