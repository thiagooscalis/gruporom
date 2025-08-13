# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from core.models import (
    Usuario, Pessoa, WhatsAppAccount, WhatsAppTemplate, 
    WhatsAppConversation, WhatsAppContact, WhatsAppMessage
)
from core.forms.whatsapp import NovoContatoForm
from core.factories import (
    PessoaFactory, UsuarioFactory, GroupFactory,
    WhatsAppAccountFactory, WhatsAppTemplateFactory, WhatsAppTemplateSimpleFactory
)


class NovoContatoTestSetupMixin:
    """Mixin para setup comum dos testes de novo contato"""
    
    def setUp(self):
        self.client = Client()
        
        # Cria usuário comercial usando factories
        self.pessoa = PessoaFactory()
        self.user = UsuarioFactory(pessoa=self.pessoa)
        self.user.set_password("senha123")
        self.user.save()
        
        # Cria grupo Comercial
        self.grupo_comercial = GroupFactory(name="Comercial")
        self.user.groups.add(self.grupo_comercial)
        
        # Adiciona permissão para controle WhatsApp se não existir
        content_type = ContentType.objects.get_for_model(WhatsAppAccount)
        permission, _ = Permission.objects.get_or_create(
            codename='controle_whatsapp',
            name='Pode controlar WhatsApp',
            content_type=content_type,
        )
        self.user.user_permissions.add(permission)
        
        # Cria conta e template WhatsApp usando factories
        self.account = WhatsAppAccountFactory(responsavel=self.user)
        self.template = WhatsAppTemplateFactory(
            account=self.account,
            name="teste_template",
            criado_por=self.user,
            body_text="Olá {{1}}, bem-vindo ao {{2}}!"
        )
        
        self.url = reverse('comercial:whatsapp_novo_contato')


class NovoContatoViewTest(NovoContatoTestSetupMixin, TestCase):
    """Testes para a view novo_contato"""
    
    def test_get_modal_form(self):
        """Testa o carregamento do modal com formulário"""
        self.client.login(username=self.user.username, password="senha123")
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Novo Contato WhatsApp")
        self.assertContains(response, "form")
        self.assertContains(response, self.template.name)
    
    def test_access_denied_without_login(self):
        """Testa que usuário não logado é redirecionado"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
    
    def test_access_denied_without_commercial_group(self):
        """Testa que usuário sem grupo Comercial é negado"""
        # Remove do grupo Comercial
        self.user.groups.clear()
        self.client.login(username=self.user.username, password="senha123")
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
    
    def test_form_validation_errors(self):
        """Testa validação de formulário com dados inválidos"""
        self.client.login(username=self.user.username, password="senha123")
        
        data = {
            'nome': '',  # Nome obrigatório
            'ddi': '55',
            'ddd': '11',
            'telefone': '999999999',
            'template_id': self.template.id
        }
        
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este campo é obrigatório")
    
    @patch('core.services.whatsapp_api.WhatsAppAPIService')
    def test_successful_contact_creation(self, mock_api_service):
        """Testa criação bem-sucedida de contato com template"""
        # Mock da API
        mock_service_instance = MagicMock()
        mock_service_instance.send_template_message.return_value = {
            'success': True,
            'message_id': 'wamid_test_123'
        }
        mock_api_service.return_value = mock_service_instance
        
        self.client.login(username=self.user.username, password="senha123")
        
        data = {
            'nome': 'Maria Silva',
            'ddi': '55',
            'ddd': '11',
            'telefone': '987654321',
            'template_id': self.template.id,
            'param_1': 'Maria',
            'param_2': 'Grupo ROM'
        }
        
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, 200)
        
        # Verifica que contato foi criado
        self.assertTrue(
            WhatsAppContact.objects.filter(
                phone_number="+5511987654321"
            ).exists()
        )
        
        # Verifica que conversa foi criada
        conversation = WhatsAppConversation.objects.filter(
            assigned_to=self.user
        ).first()
        self.assertIsNotNone(conversation)
        self.assertEqual(conversation.status, 'assigned')
        self.assertIsNotNone(conversation.first_message_at)
        self.assertIsNotNone(conversation.assigned_at)
        
        # Verifica que mensagem foi criada
        message = WhatsAppMessage.objects.filter(
            conversation=conversation
        ).first()
        self.assertIsNotNone(message)
        self.assertEqual(message.wamid, 'wamid_test_123')
        self.assertEqual(message.direction, 'outbound')
        self.assertEqual(message.message_type, 'template')
        
        # Verifica que API foi chamada com parâmetros corretos
        mock_service_instance.send_template_message.assert_called_once()
        call_args = mock_service_instance.send_template_message.call_args
        self.assertEqual(call_args[0][0], "+5511987654321")  # phone_number
        self.assertEqual(call_args[0][1], "teste_template")  # template_name
    
    @patch('core.services.whatsapp_api.WhatsAppAPIService')
    def test_api_error_handling(self, mock_api_service):
        """Testa tratamento de erro da API"""
        # Mock da API com erro
        mock_service_instance = MagicMock()
        mock_service_instance.send_template_message.return_value = {
            'success': False,
            'error': 'Template not approved'
        }
        mock_api_service.return_value = mock_service_instance
        
        self.client.login(username=self.user.username, password="senha123")
        
        data = {
            'nome': 'Maria Silva',
            'ddi': '55',
            'ddd': '11',
            'telefone': '987654321',
            'template_id': self.template.id
        }
        
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Erro ao enviar template")
        
        # Verifica que NADA foi criado devido ao erro da API
        # (contato só é criado após sucesso do envio)
        self.assertFalse(
            WhatsAppContact.objects.filter(
                phone_number="+5511987654321"
            ).exists()
        )
        
        self.assertFalse(
            WhatsAppConversation.objects.filter(
                assigned_to=self.user
            ).exists()
        )
        
        self.assertFalse(
            WhatsAppMessage.objects.exists()
        )
    
    @patch('core.services.whatsapp_api.WhatsAppAPIService')
    def test_api_exception_handling(self, mock_api_service):
        """Testa tratamento de exceção da API"""
        # Mock que lança exceção
        mock_api_service.side_effect = Exception("Connection timeout")
        
        self.client.login(username=self.user.username, password="senha123")
        
        data = {
            'nome': 'Maria Silva',
            'ddi': '55',
            'ddd': '11',
            'telefone': '987654321',
            'template_id': self.template.id
        }
        
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Erro de conexão com WhatsApp")
    
    def test_form_validation_requires_template(self):
        """Testa que template é obrigatório"""
        self.client.login(username=self.user.username, password="senha123")
        
        data = {
            'nome': 'João Teste',
            'ddi': '55',
            'ddd': '11',
            'telefone': '123456789',
            'template_id': ''  # Sem template - deve gerar erro
        }
        
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este campo é obrigatório")
        
        # Verifica que nenhum contato foi criado
        self.assertFalse(
            WhatsAppContact.objects.filter(
                phone_number="+5511123456789"
            ).exists()
        )


class TemplatePreviewViewTest(NovoContatoTestSetupMixin, TestCase):
    """Testes para a view template_preview"""
    
    def setUp(self):
        super().setUp()
        self.url = reverse('comercial:template_preview')
    
    def test_template_preview_with_params(self):
        """Testa preview de template com parâmetros"""
        self.client.login(username=self.user.username, password="senha123")
        
        response = self.client.get(self.url, {
            'template_id': self.template.id
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Preview do Template")
        self.assertContains(response, self.template.body_text)
        self.assertContains(response, "Parâmetro")
        self.assertContains(response, 'name="param_1"')
        self.assertContains(response, 'name="param_2"')
    
    def test_template_preview_without_params(self):
        """Testa preview de template sem parâmetros"""
        # Cria template sem parâmetros usando factory
        template_simples = WhatsAppTemplateSimpleFactory(
            account=self.account,
            criado_por=self.user
        )
        
        self.client.login(username=self.user.username, password="senha123")
        
        response = self.client.get(self.url, {
            'template_id': template_simples.id
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Preview do Template")
        self.assertContains(response, template_simples.body_text)
        self.assertNotContains(response, "Parâmetros do Template")
    
    def test_template_preview_empty(self):
        """Testa preview sem template_id"""
        self.client.login(username=self.user.username, password="senha123")
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        # Deve retornar template vazio
        self.assertNotContains(response, "Preview do Template")
    
    def test_template_preview_invalid_id(self):
        """Testa preview com template_id inválido"""
        self.client.login(username=self.user.username, password="senha123")
        
        response = self.client.get(self.url, {
            'template_id': 99999  # ID inexistente
        })
        
        self.assertEqual(response.status_code, 200)
        # Deve retornar template vazio
        self.assertNotContains(response, "Preview do Template")


class NovoContatoFormTest(TestCase):
    """Testes para o formulário NovoContatoForm"""
    
    def setUp(self):
        # Cria usuário para ser responsável usando factories
        self.pessoa = PessoaFactory()
        self.user = UsuarioFactory(pessoa=self.pessoa)
        
        # Cria conta e template WhatsApp usando factories
        self.account = WhatsAppAccountFactory(responsavel=self.user)
        self.template = WhatsAppTemplateFactory(
            account=self.account,
            criado_por=self.user,
            body_text="Olá {{1}}!"
        )
    
    def test_form_valid_data(self):
        """Testa formulário com dados válidos"""
        form_data = {
            'nome': 'João Silva',
            'ddi': '55',
            'ddd': '11',
            'telefone': '987654321',
            'template_id': self.template.id
        }
        
        form = NovoContatoForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_nome(self):
        """Testa formulário com nome inválido"""
        form_data = {
            'nome': '',  # Nome obrigatório
            'ddi': '55',
            'ddd': '11',
            'telefone': '987654321',
            'template_id': self.template.id
        }
        
        form = NovoContatoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)
    
    def test_form_invalid_ddi(self):
        """Testa formulário com DDI inválido"""
        form_data = {
            'nome': 'João Silva',
            'ddi': 'abc',  # DDI deve ser numérico
            'ddd': '11',
            'telefone': '987654321',
            'template_id': self.template.id
        }
        
        form = NovoContatoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('ddi', form.errors)
    
    def test_form_invalid_ddd(self):
        """Testa formulário com DDD inválido"""
        form_data = {
            'nome': 'João Silva',
            'ddi': '55',
            'ddd': '1',  # DDD deve ter 2 dígitos
            'telefone': '987654321',
            'template_id': self.template.id
        }
        
        form = NovoContatoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('ddd', form.errors)
    
    def test_form_invalid_telefone(self):
        """Testa formulário com telefone inválido"""
        form_data = {
            'nome': 'João Silva',
            'ddi': '55',
            'ddd': '11',
            'telefone': '123',  # Telefone muito curto
            'template_id': self.template.id
        }
        
        form = NovoContatoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('telefone', form.errors)
    
    def test_get_phone_number(self):
        """Testa método get_phone_number"""
        form_data = {
            'nome': 'João Silva',
            'ddi': '55',
            'ddd': '11',
            'telefone': '987654321',
            'template_id': self.template.id
        }
        
        form = NovoContatoForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        phone_number = form.get_phone_number()
        self.assertEqual(phone_number, "+5511987654321")
    
    def test_get_template_params(self):
        """Testa método get_template_params"""
        form_data = {
            'nome': 'João Silva',
            'ddi': '55',
            'ddd': '11',
            'telefone': '987654321',
            'template_id': self.template.id,
            'param_1': 'João',
            'param_2': 'Teste'
        }
        
        form = NovoContatoForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        params = form.get_template_params()
        expected_params = {1: 'João', 2: 'Teste'}
        self.assertEqual(params, expected_params)
    
    def test_template_choices_format(self):
        """Testa formato das choices do template"""
        form = NovoContatoForm()
        
        # Verifica se template aparece com formato correto
        choices = dict(form.fields['template_id'].choices)
        expected_label = f"{self.template.name} - {self.account.name}"
        self.assertIn(expected_label, choices.values())


class WhatsAppAPIServiceMockTest(TestCase):
    """Testes para garantir que mocks da API funcionam corretamente"""
    
    @patch('core.services.whatsapp_api.WhatsAppAPIService')
    def test_successful_api_mock(self, mock_api_service):
        """Testa mock bem-sucedido da API"""
        # Configura mock
        mock_service_instance = MagicMock()
        mock_service_instance.send_template_message.return_value = {
            'success': True,
            'message_id': 'wamid_mock_123'
        }
        mock_api_service.return_value = mock_service_instance
        
        # Simula chamada
        service = mock_api_service(None)
        response = service.send_template_message(
            "+5511999999999",
            "test_template",
            "pt_BR",
            []
        )
        
        self.assertTrue(response['success'])
        self.assertEqual(response['message_id'], 'wamid_mock_123')
        mock_service_instance.send_template_message.assert_called_once()
    
    @patch('core.services.whatsapp_api.WhatsAppAPIService')
    def test_failed_api_mock(self, mock_api_service):
        """Testa mock com falha da API"""
        # Configura mock com erro
        mock_service_instance = MagicMock()
        mock_service_instance.send_template_message.return_value = {
            'success': False,
            'error': 'Template not found'
        }
        mock_api_service.return_value = mock_service_instance
        
        # Simula chamada
        service = mock_api_service(None)
        response = service.send_template_message(
            "+5511999999999",
            "invalid_template",
            "pt_BR",
            []
        )
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'Template not found')
    
    @patch('core.services.whatsapp_api.WhatsAppAPIService')
    def test_api_exception_mock(self, mock_api_service):
        """Testa mock com exceção da API"""
        # Configura mock para lançar exceção
        mock_api_service.side_effect = Exception("Network error")
        
        with self.assertRaises(Exception) as context:
            mock_api_service(None)
        
        self.assertEqual(str(context.exception), "Network error")