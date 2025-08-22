from django.db import models
from datetime import timedelta
from .bloqueio import Bloqueio


class DiaRoteiro(models.Model):
    ordem = models.PositiveIntegerField(verbose_name="Ordem")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição")
    bloqueio = models.ForeignKey(Bloqueio, on_delete=models.PROTECT, verbose_name="Bloqueio")
    
    class Meta:
        verbose_name = "Dia do Roteiro"
        verbose_name_plural = "Dias do Roteiro"
        ordering = ['bloqueio', 'ordem']
        unique_together = ['bloqueio', 'ordem']
    
    def __str__(self):
        return f"Dia {self.ordem}: {self.titulo}"
    
    @property
    def data_formatada(self):
        """
        Retorna a data do dia do roteiro formatada como:
        {dia da semana} {dia}/{mês}
        Ex: Segunda-feira 15/03
        """
        try:
            # Calcula a data baseada na data de saída do bloqueio + ordem do dia
            data_dia = self.bloqueio.saida + timedelta(days=self.ordem - 1)
            
            # Dicionário para traduzir dias da semana
            dias_semana = {
                0: 'Segunda-feira',
                1: 'Terça-feira',
                2: 'Quarta-feira',
                3: 'Quinta-feira',
                4: 'Sexta-feira',
                5: 'Sábado',
                6: 'Domingo'
            }
            
            # Pega o dia da semana (0 = segunda, 6 = domingo)
            dia_semana = dias_semana.get(data_dia.weekday(), '')
            
            # Formata dia/mês
            data_formatada = data_dia.strftime('%d/%m')
            
            return f"{dia_semana} {data_formatada}"
        except:
            return f"Dia {self.ordem}"
    
    @property
    def data_completa(self):
        """
        Retorna a data completa do dia do roteiro
        """
        try:
            return self.bloqueio.saida + timedelta(days=self.ordem - 1)
        except:
            return None