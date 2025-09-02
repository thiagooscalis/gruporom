# -*- coding: utf-8 -*-
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import InMemoryStorage
from django.urls import reverse
from core.factories import (
    UsuarioFactory, GroupFactory, WhatsAppAccountFactory, 
    WhatsAppConversationFactory, WhatsAppContactFactory
)
from core.models import Usuario, WhatsAppConversation


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class ComercialWhatsAppViewsTest(TestCase):
    
    def setUp(self):
        """Configura dados para os testes"""
        self.client = Client()
        
        # Criar grupo comercial
        self.grupo_comercial = GroupFactory(name='Comercial')
        
        # Criar permissão controle_whatsapp
        content_type = ContentType.objects.get_for_model(Usuario)
        self.perm_whatsapp = Permission.objects.create(
            codename='controle_whatsapp',
            name='Pode gerenciar WhatsApp Business',
            content_type=content_type
        )
        
        # Criar usuário comercial com permissão WhatsApp
        self.user_comercial_whatsapp = UsuarioFactory()
        self.user_comercial_whatsapp.groups.add(self.grupo_comercial)
        self.user_comercial_whatsapp.user_permissions.add(self.perm_whatsapp)
        
        # Criar usuário comercial sem permissão WhatsApp
        self.user_comercial_sem_whatsapp = UsuarioFactory()
        self.user_comercial_sem_whatsapp.groups.add(self.grupo_comercial)
        
        # Fazer login do usuário com permissões completas
        self.client.force_login(self.user_comercial_whatsapp)
        
        # Criar conta WhatsApp para testes
        self.whatsapp_account = WhatsAppAccountFactory(is_active=True)
        self.contact = WhatsAppContactFactory()
    
    def test_whatsapp_geral_acesso_autorizado(self):
        """Testa acesso à página WhatsApp geral"""
        response = self.client.get(reverse('comercial:whatsapp_geral'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('stats', response.context)
    
    def test_whatsapp_geral_acesso_negado_sem_permissao(self):
        """Testa negação de acesso sem permissão WhatsApp"""
        self.client.force_login(self.user_comercial_sem_whatsapp)
        response = self.client.get(reverse('comercial:whatsapp_geral'))
        
        self.assertIn(response.status_code, [302, 403])
    
    def test_whatsapp_geral_com_conversas(self):
        """Testa página com conversas existentes"""
        WhatsAppConversationFactory(
            status='pending',
            account=self.whatsapp_account,
            contact=self.contact
        )
        WhatsAppConversationFactory(
            status='assigned',
            account=self.whatsapp_account,
            contact=WhatsAppContactFactory(),
            assigned_to=self.user_comercial_whatsapp
        )
        
        response = self.client.get(reverse('comercial:whatsapp_geral'))
        
        self.assertEqual(response.status_code, 200)
        stats = response.context['stats']
        self.assertEqual(stats['total'], 2)
        self.assertEqual(stats['pending'], 1)
        self.assertEqual(stats['assigned'], 1)
    
    def test_conversations_table_htmx(self):
        """Testa endpoint HTMX de tabela de conversas"""
        WhatsAppConversationFactory(
            status='pending',
            account=self.whatsapp_account,
            contact=self.contact
        )
        
        response = self.client.get(reverse('comercial:conversations_table'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['pending_conversations']), 1)
    
    def test_my_conversations_htmx(self):
        """Testa endpoint HTMX de minhas conversas"""
        WhatsAppConversationFactory(
            status='in_progress',
            account=self.whatsapp_account,
            contact=self.contact,
            assigned_to=self.user_comercial_whatsapp
        )
        
        response = self.client.get(reverse('comercial:my_conversations'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['my_conversations']), 1)
    
    def test_pending_conversations_htmx(self):
        """Testa endpoint HTMX de conversas pendentes"""
        WhatsAppConversationFactory(
            status='pending',
            account=self.whatsapp_account,
            contact=self.contact
        )
        WhatsAppConversationFactory(
            status='assigned',
            account=self.whatsapp_account,
            contact=WhatsAppContactFactory()
        )
        
        response = self.client.get(reverse('comercial:pending_conversations'))
        self.assertEqual(response.status_code, 200)
        # Deve retornar apenas conversas pendentes
        self.assertEqual(len(response.context['pending_conversations']), 1)


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class WhatsAppPermissionsTest(TestCase):
    """Testes de controle de permissões WhatsApp"""
    
    def setUp(self):
        self.client = Client()
        self.grupo_comercial = GroupFactory(name='Comercial')
        
        # Criar permissão
        content_type = ContentType.objects.get_for_model(Usuario)
        self.perm_whatsapp = Permission.objects.create(
            codename='controle_whatsapp',
            name='Pode gerenciar WhatsApp Business',
            content_type=content_type
        )
        
        # Usuários com diferentes permissões
        self.user_com_whatsapp = UsuarioFactory()
        self.user_com_whatsapp.groups.add(self.grupo_comercial)
        self.user_com_whatsapp.user_permissions.add(self.perm_whatsapp)
        
        self.user_sem_whatsapp = UsuarioFactory()
        self.user_sem_whatsapp.groups.add(self.grupo_comercial)
    
    def test_whatsapp_geral_requires_permission(self):
        """Testa que whatsapp_geral requer permissão especial"""
        # Com permissão - deve funcionar
        self.client.force_login(self.user_com_whatsapp)
        response = self.client.get(reverse('comercial:whatsapp_geral'))
        self.assertEqual(response.status_code, 200)
        
        # Sem permissão - deve ser negado
        self.client.force_login(self.user_sem_whatsapp)
        response = self.client.get(reverse('comercial:whatsapp_geral'))
        self.assertIn(response.status_code, [302, 403])
    
    def test_outras_views_whatsapp_apenas_comercial(self):
        """Testa que outras views requerem apenas grupo Comercial"""
        urls_apenas_comercial = [
            'comercial:conversations_table',
            'comercial:my_conversations',
            'comercial:pending_conversations',
        ]
        
        # Usuário comercial sem permissão WhatsApp - deve funcionar
        self.client.force_login(self.user_sem_whatsapp)
        
        for url_name in urls_apenas_comercial:
            with self.subTest(url=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)