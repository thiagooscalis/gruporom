# -*- coding: utf-8 -*-
import pytest
from datetime import time
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from core.models import Turno


@pytest.mark.django_db
class TestTurnoModel:
    """Tests para o modelo Turno"""

    def test_create_turno(self):
        """Testa criação básica de turno"""
        turno = Turno.objects.create(
            nome="Manhã",
            inicio=time(8, 0),
            fim=time(12, 0)
        )
        
        assert turno.nome == "Manhã"
        assert turno.inicio == time(8, 0)
        assert turno.fim == time(12, 0)
        assert turno.ativo is True  # Default
        assert str(turno) == "Manhã (08:00 - 12:00)"

    def test_clean_nome_formatado(self):
        """Testa que o nome é formatado com title()"""
        turno = Turno.objects.create(
            nome="tarde",
            inicio=time(13, 0),
            fim=time(17, 0)
        )
        
        assert turno.nome == "Tarde"

    def test_clean_nome_com_espacos(self):
        """Testa que espaços extras são removidos do nome"""
        turno = Turno.objects.create(
            nome="  noite  ",
            inicio=time(18, 0),
            fim=time(22, 0)
        )
        
        assert turno.nome == "Noite"

    def test_nome_unico(self):
        """Testa que nome deve ser único"""
        # Cria primeiro turno
        Turno.objects.create(
            nome="Especial",
            inicio=time(9, 0),
            fim=time(15, 0)
        )
        
        # Tenta criar turno com mesmo nome
        with pytest.raises(IntegrityError):
            Turno.objects.create(
                nome="Especial",
                inicio=time(10, 0),
                fim=time(16, 0)
            )

    def test_clean_horarios_iguais(self):
        """Testa validação de horários iguais"""
        turno = Turno(
            nome="Inválido",
            inicio=time(10, 0),
            fim=time(10, 0)
        )
        
        with pytest.raises(ValidationError) as exc_info:
            turno.clean()
        
        assert "não podem ser iguais" in str(exc_info.value)

    def test_save_executa_clean(self):
        """Testa que save() executa clean() automaticamente"""
        turno = Turno(
            nome="teste save",
            inicio=time(12, 0),
            fim=time(12, 0)
        )
        
        with pytest.raises(ValidationError):
            turno.save()

    def test_duracao_horas_normal(self):
        """Testa cálculo de duração para turno normal"""
        turno = Turno.objects.create(
            nome="Comercial",
            inicio=time(9, 0),
            fim=time(17, 0)
        )
        
        assert turno.duracao_horas == 8.0

    def test_duracao_horas_com_minutos(self):
        """Testa cálculo de duração com minutos"""
        turno = Turno.objects.create(
            nome="Meio Período",
            inicio=time(14, 30),
            fim=time(18, 45)
        )
        
        assert turno.duracao_horas == 4.25  # 4h15min = 4.25h

    def test_duracao_horas_noturno(self):
        """Testa cálculo de duração para turno noturno"""
        turno = Turno.objects.create(
            nome="Madrugada",
            inicio=time(22, 0),
            fim=time(6, 0)
        )
        
        assert turno.duracao_horas == 8.0

    def test_eh_noturno_false(self):
        """Testa property eh_noturno para turno diurno"""
        turno = Turno.objects.create(
            nome="Diurno",
            inicio=time(8, 0),
            fim=time(16, 0)
        )
        
        assert turno.eh_noturno is False

    def test_eh_noturno_true(self):
        """Testa property eh_noturno para turno noturno"""
        turno = Turno.objects.create(
            nome="Noturno",
            inicio=time(23, 0),
            fim=time(7, 0)
        )
        
        assert turno.eh_noturno is True

    def test_ativo_default_true(self):
        """Testa que ativo vem True por padrão"""
        turno = Turno.objects.create(
            nome="Padrão",
            inicio=time(10, 0),
            fim=time(14, 0)
        )
        
        assert turno.ativo is True

    def test_ativo_pode_ser_false(self):
        """Testa turno inativo"""
        turno = Turno.objects.create(
            nome="Inativo",
            inicio=time(6, 0),
            fim=time(12, 0),
            ativo=False
        )
        
        assert turno.ativo is False

    def test_total_funcionarios_property(self):
        """Testa property total_funcionarios"""
        turno = Turno.objects.create(
            nome="Teste",
            inicio=time(8, 0),
            fim=time(17, 0)
        )
        
        # Por enquanto retorna 0 (será implementado com model de funcionários)
        assert turno.total_funcionarios == 0

    def test_get_turnos_ativos(self):
        """Testa método get_turnos_ativos"""
        # Cria turnos ativos e inativos
        Turno.objects.create(nome="Ativo 1", inicio=time(8, 0), fim=time(12, 0), ativo=True)
        Turno.objects.create(nome="Ativo 2", inicio=time(13, 0), fim=time(17, 0), ativo=True)
        Turno.objects.create(nome="Inativo", inicio=time(18, 0), fim=time(22, 0), ativo=False)
        
        turnos_ativos = Turno.get_turnos_ativos()
        
        assert turnos_ativos.count() == 2
        assert all(turno.ativo for turno in turnos_ativos)

    def test_criar_turnos_padrao(self):
        """Testa método criar_turnos_padrao"""
        # Limpa turnos existentes
        Turno.objects.all().delete()
        
        turnos_criados = Turno.criar_turnos_padrao()
        
        assert len(turnos_criados) == 4
        assert Turno.objects.count() == 4
        
        # Verifica se turnos específicos foram criados
        assert Turno.objects.filter(nome="Manhã").exists()
        assert Turno.objects.filter(nome="Tarde").exists()
        assert Turno.objects.filter(nome="Noite").exists()
        assert Turno.objects.filter(nome="Madrugada").exists()

    def test_criar_turnos_padrao_nao_duplica(self):
        """Testa que criar_turnos_padrao não duplica turnos existentes"""
        # Cria um turno manualmente
        Turno.objects.create(nome="Manhã", inicio=time(8, 0), fim=time(12, 0))
        
        turnos_criados = Turno.criar_turnos_padrao()
        
        # Deve criar apenas os 3 restantes
        assert len(turnos_criados) == 3
        assert Turno.objects.filter(nome="Manhã").count() == 1  # Não duplicou

    def test_ordenacao_padrao(self):
        """Testa ordenação padrão por horário de início"""
        # Cria turnos fora de ordem
        Turno.objects.create(nome="Tarde", inicio=time(14, 0), fim=time(18, 0))
        Turno.objects.create(nome="Manhã", inicio=time(8, 0), fim=time(12, 0))
        Turno.objects.create(nome="Noite", inicio=time(20, 0), fim=time(23, 59))
        
        turnos = list(Turno.objects.all())
        horarios_inicio = [turno.inicio for turno in turnos]
        
        # Deve estar ordenado por horário de início
        assert horarios_inicio == [time(8, 0), time(14, 0), time(20, 0)]

    def test_campos_timestamp(self):
        """Testa campos de timestamp"""
        turno = Turno.objects.create(
            nome="Timestamp",
            inicio=time(9, 0),
            fim=time(17, 0)
        )
        
        assert turno.criado_em is not None
        assert turno.atualizado_em is not None
        assert turno.criado_em <= turno.atualizado_em

    def test_meta_informacoes(self):
        """Testa informações do Meta do modelo"""
        meta = Turno._meta
        
        assert meta.verbose_name == "Turno"
        assert meta.verbose_name_plural == "Turnos"
        assert meta.ordering == ['inicio']