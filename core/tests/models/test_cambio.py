# -*- coding: utf-8 -*-
import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch, Mock
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from core.models import Cambio


@pytest.mark.django_db
class TestCambioModel:
    """Tests para o modelo Cambio"""

    def test_create_cambio(self):
        """Testa criação básica de câmbio"""
        data_teste = date.today()
        valor_teste = Decimal('5.2345')
        
        cambio = Cambio.objects.create(
            data=data_teste,
            valor=valor_teste
        )
        
        assert cambio.data == data_teste
        assert cambio.valor == valor_teste
        assert str(cambio) == f"USD/BRL {data_teste.strftime('%d/%m/%Y')}: R$ {valor_teste}"

    def test_data_unica(self):
        """Testa que a data deve ser única"""
        data_teste = date.today()
        
        # Cria primeiro câmbio
        Cambio.objects.create(data=data_teste, valor=Decimal('5.0000'))
        
        # Tenta criar segundo câmbio com mesma data
        with pytest.raises(IntegrityError):
            Cambio.objects.create(data=data_teste, valor=Decimal('5.1000'))

    def test_clean_valor_positivo(self):
        """Testa validação de valor positivo"""
        cambio = Cambio(data=date.today(), valor=Decimal('-1.0000'))
        
        with pytest.raises(ValidationError) as exc_info:
            cambio.clean()
        
        assert "O valor do câmbio deve ser maior que zero" in str(exc_info.value)

    def test_clean_valor_zero(self):
        """Testa validação de valor zero"""
        cambio = Cambio(data=date.today(), valor=Decimal('0.0000'))
        
        with pytest.raises(ValidationError):
            cambio.clean()

    @patch('core.models.cambio.requests.get')
    def test_buscar_cambio_awesomeapi_sucesso_atual(self, mock_get):
        """Testa busca bem-sucedida na AwesomeAPI para data atual"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.json.return_value = {
            'USDBRL': {
                'bid': '5.2345',
                'ask': '5.2355'
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        valor = Cambio.buscar_cambio_awesomeapi(date.today())
        
        assert valor == Decimal('5.2345')
        mock_get.assert_called_once()

    @patch('core.models.cambio.requests.get')
    def test_buscar_cambio_awesomeapi_sucesso_historico(self, mock_get):
        """Testa busca bem-sucedida na AwesomeAPI para data histórica"""
        data_ontem = date.today() - timedelta(days=1)
        
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                'bid': '5.1234',
                'ask': '5.1244'
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        valor = Cambio.buscar_cambio_awesomeapi(data_ontem)
        
        assert valor == Decimal('5.1234')
        mock_get.assert_called_once()

    @patch('core.models.cambio.requests.get')
    def test_buscar_cambio_awesomeapi_erro_request(self, mock_get):
        """Testa erro na requisição da AwesomeAPI"""
        mock_get.side_effect = Exception("Erro de conexão")
        
        valor = Cambio.buscar_cambio_awesomeapi()
        
        assert valor is None

    @patch('core.models.cambio.requests.get')
    def test_buscar_cambio_awesomeapi_dados_invalidos(self, mock_get):
        """Testa resposta com dados inválidos da AwesomeAPI"""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        valor = Cambio.buscar_cambio_awesomeapi()
        
        assert valor is None

    def test_obter_cambio_existente(self):
        """Testa obtenção de câmbio que já existe no banco"""
        data_teste = date.today()
        valor_teste = Decimal('5.3333')
        
        # Cria câmbio no banco
        cambio_original = Cambio.objects.create(data=data_teste, valor=valor_teste)
        
        # Obtém câmbio
        cambio_obtido = Cambio.obter_cambio(data_teste)
        
        assert cambio_obtido.id == cambio_original.id
        assert cambio_obtido.valor == valor_teste

    @patch('core.models.cambio.Cambio.buscar_cambio_awesomeapi')
    def test_obter_cambio_nao_existente_sucesso_api(self, mock_buscar_api):
        """Testa obtenção de câmbio não existente com sucesso na API"""
        data_teste = date.today() - timedelta(days=10)  # Data que não existe
        valor_api = Decimal('5.4444')
        
        mock_buscar_api.return_value = valor_api
        
        cambio = Cambio.obter_cambio(data_teste)
        
        assert cambio is not None
        assert cambio.data == data_teste
        assert cambio.valor == valor_api
        assert Cambio.objects.filter(data=data_teste).exists()

    @patch('core.models.cambio.Cambio.buscar_cambio_awesomeapi')
    def test_obter_cambio_nao_existente_falha_api(self, mock_buscar_api):
        """Testa obtenção de câmbio não existente com falha na API"""
        data_teste = date.today() - timedelta(days=10)
        
        mock_buscar_api.return_value = None
        
        cambio = Cambio.obter_cambio(data_teste)
        
        assert cambio is None

    def test_obter_valor_cambio(self):
        """Testa método de conveniência obter_valor_cambio"""
        data_teste = date.today()
        valor_teste = Decimal('5.5555')
        
        Cambio.objects.create(data=data_teste, valor=valor_teste)
        
        valor = Cambio.obter_valor_cambio(data_teste)
        
        assert valor == valor_teste

    def test_obter_valor_cambio_nao_encontrado(self):
        """Testa obter_valor_cambio quando não encontra câmbio"""
        data_inexistente = date.today() - timedelta(days=100)
        
        with patch('core.models.cambio.Cambio.obter_cambio') as mock_obter:
            mock_obter.return_value = None
            
            valor = Cambio.obter_valor_cambio(data_inexistente)
            
            assert valor is None

    def test_ordenacao_padrao(self):
        """Testa ordenação padrão por data decrescente"""
        data1 = date.today() - timedelta(days=2)
        data2 = date.today() - timedelta(days=1)
        data3 = date.today()
        
        # Cria câmbios fora de ordem
        Cambio.objects.create(data=data2, valor=Decimal('5.2'))
        Cambio.objects.create(data=data3, valor=Decimal('5.3'))
        Cambio.objects.create(data=data1, valor=Decimal('5.1'))
        
        cambios = list(Cambio.objects.all())
        
        # Deve estar ordenado por data decrescente
        assert cambios[0].data == data3
        assert cambios[1].data == data2
        assert cambios[2].data == data1

    def test_save_com_validacao(self):
        """Testa que save() chama clean() para validação"""
        cambio = Cambio(data=date.today(), valor=Decimal('-1.0'))
        
        with pytest.raises(ValidationError):
            cambio.save()

    def test_meta_informacoes(self):
        """Testa informações do Meta do modelo"""
        meta = Cambio._meta
        
        assert meta.verbose_name == "Câmbio"
        assert meta.verbose_name_plural == "Câmbios"
        assert meta.ordering == ['-data']