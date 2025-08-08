from django.db import models


class Funcao(models.Model):
    masculino = models.CharField(max_length=100, verbose_name="Título Masculino")
    feminino = models.CharField(max_length=100, verbose_name="Título Feminino")
    abreviacao_masculino = models.CharField(max_length=20, verbose_name="Abrev. de Título Masculino")
    abreviacao_feminino = models.CharField(max_length=20, verbose_name="Abrev. de Título Feminino")
    
    class Meta:
        verbose_name = "Função"
        verbose_name_plural = "Funções"
        ordering = ['masculino']
    
    def __str__(self):
        return f"{self.masculino} / {self.feminino}"
    
    def get_funcao_por_sexo(self, sexo):
        """
        Retorna a função conforme o sexo informado
        
        Args:
            sexo (str): 'Masculino' ou 'Feminino' (conforme SEXO_CHOICES)
        
        Returns:
            str: A função no gênero correto
        """
        if sexo == 'Feminino':
            return self.feminino
        return self.masculino
    
    def get_abreviacao_por_sexo(self, sexo):
        """
        Retorna a abreviação conforme o sexo informado
        
        Args:
            sexo (str): 'Masculino' ou 'Feminino' (conforme SEXO_CHOICES)
        
        Returns:
            str: A abreviação no gênero correto
        """
        if sexo == 'Feminino':
            return self.abreviacao_feminino
        return self.abreviacao_masculino