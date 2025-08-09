# -*- coding: utf-8 -*-
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from core.models import Cargo, Pessoa


@pytest.mark.django_db
class TestCargoModel:
    """Tests para o modelo Cargo"""

    @pytest.fixture
    def empresa_gruporom(self):
        """Fixture para empresa do Grupo ROM"""
        from core.factories import EmpresaGrupoROMFactory
        return EmpresaGrupoROMFactory(
            doc="12345678000195",
            nome="US Travel Operadora"
        )

    @pytest.fixture
    def empresa_normal(self):
        """Fixture para empresa que não é do Grupo ROM"""
        from core.factories import PessoaJuridicaFactory
        return PessoaJuridicaFactory(
            doc="98765432000187",
            nome="Empresa Externa",
            empresa_gruporom=False
        )

    def test_create_cargo(self, empresa_gruporom):
        """Testa criação básica de cargo"""
        cargo = Cargo.objects.create(
            nome="Diretor Executivo",
            empresa=empresa_gruporom
        )
        
        assert cargo.nome == "Diretor Executivo"
        assert cargo.empresa == empresa_gruporom
        assert cargo.ativo is True  # Default
        assert str(cargo) == "Diretor Executivo - US Travel Operadora"

    def test_clean_nome_formatado(self, empresa_gruporom):
        """Testa que o nome é formatado com title()"""
        cargo = Cargo.objects.create(
            nome="gerente de vendas",
            empresa=empresa_gruporom
        )
        
        assert cargo.nome == "Gerente De Vendas"

    def test_clean_nome_com_espacos(self, empresa_gruporom):
        """Testa que espaços nas pontas são removidos e nome é formatado"""
        cargo = Cargo.objects.create(
            nome="  analista de marketing  ",
            empresa=empresa_gruporom
        )
        
        # strip() remove espaços das pontas, title() formata
        assert cargo.nome == "Analista De Marketing"

    def test_unique_together_nome_empresa(self, empresa_gruporom):
        """Testa que não pode ter cargo duplicado na mesma empresa"""
        # Cria primeiro cargo
        Cargo.objects.create(
            nome="Gerente Geral",
            empresa=empresa_gruporom
        )
        
        # Tenta criar cargo com mesmo nome na mesma empresa
        with pytest.raises(IntegrityError):
            Cargo.objects.create(
                nome="Gerente Geral",
                empresa=empresa_gruporom
            )

    def test_mesmo_nome_empresas_diferentes(self):
        """Testa que pode ter mesmo cargo em empresas diferentes"""
        from core.factories import EmpresaGrupoROMFactory
        empresa1 = EmpresaGrupoROMFactory(
            doc="11111111000111",
            nome="Empresa ROM 1",
        )
        empresa2 = EmpresaGrupoROMFactory(
            doc="22222222000122",
            nome="Empresa ROM 2",
        )
        
        # Cria mesmo cargo em empresas diferentes
        cargo1 = Cargo.objects.create(nome="Diretor", empresa=empresa1)
        cargo2 = Cargo.objects.create(nome="Diretor", empresa=empresa2)
        
        assert cargo1.nome == cargo2.nome
        assert cargo1.empresa != cargo2.empresa

    def test_clean_empresa_nao_gruporom(self, empresa_normal):
        """Testa validação de empresa que não é do Grupo ROM"""
        cargo = Cargo(
            nome="Gerente",
            empresa=empresa_normal
        )
        
        with pytest.raises(ValidationError) as exc_info:
            cargo.clean()
        
        assert "deve ser vinculado a uma empresa do Grupo ROM" in str(exc_info.value)

    def test_ativo_default_true(self, empresa_gruporom):
        """Testa que ativo vem True por padrão"""
        cargo = Cargo.objects.create(
            nome="Coordenador",
            empresa=empresa_gruporom
        )
        
        assert cargo.ativo is True

    def test_ativo_pode_ser_false(self, empresa_gruporom):
        """Testa cargo inativo"""
        cargo = Cargo.objects.create(
            nome="Assistente",
            empresa=empresa_gruporom,
            ativo=False
        )
        
        assert cargo.ativo is False

    def test_delete_empresa_protegido(self, empresa_gruporom):
        """Testa que não pode deletar empresa que tem cargos"""
        cargo = Cargo.objects.create(
            nome="CEO",
            empresa=empresa_gruporom
        )
        
        # Tenta deletar empresa - deve falhar (PROTECT)
        with pytest.raises(Exception):
            empresa_gruporom.delete()

    def test_ordenacao_padrao(self):
        """Testa ordenação padrão por empresa e nome"""
        # Cria empresas
        from core.factories import EmpresaGrupoROMFactory
        empresa1 = EmpresaGrupoROMFactory(
            doc="33333333000133",
            nome="A Empresa ROM",
        )
        empresa2 = EmpresaGrupoROMFactory(
            doc="44444444000144",
            nome="B Empresa ROM",
        )
        
        # Cria cargos fora de ordem
        Cargo.objects.create(nome="Zelador", empresa=empresa2)
        Cargo.objects.create(nome="Analista", empresa=empresa1)
        Cargo.objects.create(nome="Gerente", empresa=empresa1)
        Cargo.objects.create(nome="Diretor", empresa=empresa2)
        
        # Busca todos ordenados
        cargos = list(Cargo.objects.all())
        cargos_str = [f"{c.empresa.nome}-{c.nome}" for c in cargos]
        
        expected = [
            "A Empresa ROM-Analista",
            "A Empresa ROM-Gerente",
            "B Empresa ROM-Diretor",
            "B Empresa ROM-Zelador"
        ]
        
        assert cargos_str == expected

    def test_total_funcionarios_property(self, empresa_gruporom):
        """Testa property total_funcionarios"""
        cargo = Cargo.objects.create(
            nome="Desenvolvedor",
            empresa=empresa_gruporom
        )
        
        # Por enquanto retorna 0 (será implementado com model de funcionários)
        assert cargo.total_funcionarios == 0

    def test_save_executa_clean(self, empresa_normal):
        """Testa que save() executa clean() automaticamente"""
        cargo = Cargo(
            nome="teste",
            empresa=empresa_normal
        )
        
        # save() deve chamar clean() e falhar
        with pytest.raises(ValidationError):
            cargo.save()

    def test_campos_timestamp(self, empresa_gruporom):
        """Testa campos de timestamp"""
        cargo = Cargo.objects.create(
            nome="Estagiário",
            empresa=empresa_gruporom
        )
        
        assert cargo.criado_em is not None
        assert cargo.atualizado_em is not None
        assert cargo.criado_em <= cargo.atualizado_em

    def test_meta_informacoes(self):
        """Testa informações do Meta do modelo"""
        meta = Cargo._meta
        
        assert meta.verbose_name == "Cargo"
        assert meta.verbose_name_plural == "Cargos"
        assert meta.ordering == ['empresa', 'nome']
        assert meta.unique_together == (('nome', 'empresa'),)