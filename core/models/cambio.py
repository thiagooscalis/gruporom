# -*- coding: utf-8 -*-
import requests
from datetime import date, datetime
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class Cambio(models.Model):
    """
    Model para armazenar cotações de câmbio do dólar
    A data deve ser única e caso não exista, busca automaticamente da AwesomeAPI
    """
    data = models.DateField(
        unique=True,
        verbose_name="Data",
        help_text="Data da cotação do câmbio"
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        verbose_name="Valor do Dólar",
        help_text="Cotação do dólar em reais (ex: 5.2345)"
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Câmbio"
        verbose_name_plural = "Câmbios"
        ordering = ['-data']

    def __str__(self):
        return f"USD/BRL {self.data.strftime('%d/%m/%Y')}: R$ {self.valor}"

    def clean(self):
        """Valida os dados do modelo"""
        if self.valor is not None and self.valor <= 0:
            raise ValidationError("O valor do câmbio deve ser maior que zero.")

    @staticmethod
    def buscar_cambio_awesomeapi(data_consulta=None):
        """
        Busca cotação do dólar na AwesomeAPI
        Se data_consulta não fornecida, usa data atual
        """
        if data_consulta is None:
            data_consulta = date.today()
        
        try:
            # Formata data para o formato da API (YYYYMMDD)
            data_formatada = data_consulta.strftime('%Y%m%d')
            
            # URL da AwesomeAPI para cotação histórica
            # Se for data atual, usa endpoint sem data
            if data_consulta == date.today():
                url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
            else:
                url = f"https://economia.awesomeapi.com.br/json/daily/USD-BRL/?start_date={data_formatada}&end_date={data_formatada}"
            
            logger.info(f"Buscando câmbio na AwesomeAPI: {url}")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Processa resposta baseada no endpoint usado
            if data_consulta == date.today():
                # Endpoint atual retorna objeto único
                usd_brl = data.get('USDBRL')
                if usd_brl:
                    valor = Decimal(usd_brl['bid'])  # 'bid' é o valor de compra
                    return valor
            else:
                # Endpoint histórico retorna lista
                if isinstance(data, list) and len(data) > 0:
                    usd_brl = data[0]
                    valor = Decimal(usd_brl['bid'])
                    return valor
            
            logger.warning(f"Dados não encontrados na AwesomeAPI para {data_consulta}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição à AwesomeAPI: {e}")
            return None
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Erro ao processar dados da AwesomeAPI: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar câmbio: {e}")
            return None

    @classmethod
    def obter_cambio(cls, data_consulta=None):
        """
        Obtém cotação do câmbio para uma data específica
        Se não existir no banco, busca na AwesomeAPI e salva
        """
        if data_consulta is None:
            data_consulta = date.today()
        
        # Tenta encontrar no banco primeiro
        try:
            cambio = cls.objects.get(data=data_consulta)
            logger.info(f"Câmbio encontrado no banco para {data_consulta}: R$ {cambio.valor}")
            return cambio
        except cls.DoesNotExist:
            pass
        
        # Se não encontrou, busca na API
        logger.info(f"Câmbio não encontrado no banco para {data_consulta}, buscando na AwesomeAPI...")
        valor_api = cls.buscar_cambio_awesomeapi(data_consulta)
        
        if valor_api is not None:
            try:
                # Cria novo registro
                cambio = cls.objects.create(
                    data=data_consulta,
                    valor=valor_api
                )
                logger.info(f"Câmbio salvo no banco para {data_consulta}: R$ {cambio.valor}")
                return cambio
            except Exception as e:
                logger.error(f"Erro ao salvar câmbio no banco: {e}")
                # Retorna objeto temporário sem salvar
                return cls(data=data_consulta, valor=valor_api)
        
        logger.warning(f"Não foi possível obter câmbio para {data_consulta}")
        return None

    @classmethod
    def obter_valor_cambio(cls, data_consulta=None):
        """
        Retorna apenas o valor do câmbio para uma data
        Método de conveniência
        """
        cambio = cls.obter_cambio(data_consulta)
        return cambio.valor if cambio else None

    def save(self, *args, **kwargs):
        """Override save para validação"""
        self.clean()
        super().save(*args, **kwargs)