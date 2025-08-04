# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError
from datetime import time


class Turno(models.Model):
    """
    Model para representar turnos de trabalho
    """
    nome = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nome do Turno",
        help_text="Ex: Manhã, Tarde, Noite, Madrugada"
    )
    inicio = models.TimeField(
        verbose_name="Horário de Início",
        help_text="Horário de início do turno (ex: 08:00)"
    )
    fim = models.TimeField(
        verbose_name="Horário de Fim",
        help_text="Horário de fim do turno (ex: 17:00)"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Turnos inativos não aparecem em novas seleções"
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        ordering = ['inicio']

    def __str__(self):
        return f"{self.nome} ({self.inicio.strftime('%H:%M')} - {self.fim.strftime('%H:%M')})"

    def clean(self):
        """Validações customizadas"""
        if self.nome:
            self.nome = self.nome.strip().title()
        
        # Valida se horário de fim é depois do início
        if self.inicio and self.fim:
            # Para turnos que passam da meia-noite (ex: 22:00 - 06:00)
            # consideramos válido se fim < início
            if self.inicio == self.fim:
                raise ValidationError("Horário de início e fim não podem ser iguais.")

    def save(self, *args, **kwargs):
        """Override save para executar clean"""
        self.clean()
        super().save(*args, **kwargs)

    @property
    def duracao_horas(self):
        """Retorna a duração do turno em horas"""
        from datetime import datetime, timedelta
        
        inicio_dt = datetime.combine(datetime.today(), self.inicio)
        fim_dt = datetime.combine(datetime.today(), self.fim)
        
        # Se fim é menor que início, assumimos que passa para o próximo dia
        if fim_dt <= inicio_dt:
            fim_dt += timedelta(days=1)
        
        duracao = fim_dt - inicio_dt
        return duracao.total_seconds() / 3600  # Retorna em horas

    @property
    def eh_noturno(self):
        """Verifica se é um turno noturno (passa da meia-noite)"""
        return self.fim < self.inicio

    @property
    def total_funcionarios(self):
        """Retorna total de funcionários neste turno"""
        # Será implementado quando houver model de funcionários
        return 0

    @classmethod
    def get_turnos_ativos(cls):
        """Retorna apenas turnos ativos"""
        return cls.objects.filter(ativo=True)

    @classmethod
    def criar_turnos_padrao(cls):
        """Cria turnos padrão se não existirem"""
        turnos_padrao = [
            {"nome": "Manhã", "inicio": time(8, 0), "fim": time(12, 0)},
            {"nome": "Tarde", "inicio": time(13, 0), "fim": time(17, 0)},
            {"nome": "Noite", "inicio": time(18, 0), "fim": time(22, 0)},
            {"nome": "Madrugada", "inicio": time(22, 0), "fim": time(6, 0)},
        ]
        
        turnos_criados = []
        for turno_data in turnos_padrao:
            turno, created = cls.objects.get_or_create(
                nome=turno_data["nome"],
                defaults={
                    "inicio": turno_data["inicio"],
                    "fim": turno_data["fim"]
                }
            )
            if created:
                turnos_criados.append(turno)
        
        return turnos_criados