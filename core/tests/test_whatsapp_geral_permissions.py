# -*- coding: utf-8 -*-
"""
Testes para controle de acesso da página WhatsApp Geral
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Group
from core.models import Usuario, Pessoa


class WhatsAppGeralPermissionsTestCase(TestCase):
    def setUp(self):
        """Configura dados para os testes"""
        # Cria pessoas
        self.pessoa_gerente = Pessoa.objects.create(
            nome="João Gerente",
            tipo_doc="cpf",
            doc="12345678901"
        )
        
        self.pessoa_atendente = Pessoa.objects.create(
            nome="Maria Atendente", 
            tipo_doc="cpf",
            doc="98765432100"
        )
        
        # Cria grupo Comercial
        self.grupo_comercial = Group.objects.create(name='Comercial')
        
        # Cria usuário gerente comercial (com permissão)
        self.usuario_gerente = Usuario.objects.create_user(
            username="gerente",
            password="senha123",
            pessoa=self.pessoa_gerente,
            gerente_comercial=True  # Isso dará a permissão controle_whatsapp
        )
        self.usuario_gerente.groups.add(self.grupo_comercial)
        
        # Cria usuário atendente comum (sem permissão)
        self.usuario_atendente = Usuario.objects.create_user(
            username="atendente",
            password="senha123", 
            pessoa=self.pessoa_atendente,
            gerente_comercial=False  # Sem permissão
        )
        self.usuario_atendente.groups.add(self.grupo_comercial)
        
        self.client = Client()

    def test_gerente_pode_acessar_whatsapp_geral(self):
        """Testa se usuário com permissão controle_whatsapp pode acessar WhatsApp Geral"""
        self.client.login(username="gerente", password="senha123")
        
        # Verifica se tem a permissão
        self.assertTrue(self.usuario_gerente.has_perm('core.controle_whatsapp'))
        
        # Tenta acessar a página
        response = self.client.get(reverse('comercial:whatsapp_geral'))
        self.assertEqual(response.status_code, 200)

    def test_atendente_nao_pode_acessar_whatsapp_geral(self):
        """Testa se usuário sem permissão controle_whatsapp não pode acessar WhatsApp Geral"""
        self.client.login(username="atendente", password="senha123")
        
        # Verifica se NÃO tem a permissão
        self.assertFalse(self.usuario_atendente.has_perm('core.controle_whatsapp'))
        
        # Tenta acessar a página - deve ser negado
        response = self.client.get(reverse('comercial:whatsapp_geral'))
        self.assertEqual(response.status_code, 302)  # Redirect de acesso negado

    def test_usuario_sem_grupo_comercial_nao_pode_acessar(self):
        """Testa se usuário sem grupo Comercial não pode acessar (mesmo com permissão)"""
        # Cria usuário com permissão mas sem grupo Comercial
        pessoa_admin = Pessoa.objects.create(
            nome="Admin Sistema",
            tipo_doc="cpf", 
            doc="11111111111"
        )
        
        usuario_admin = Usuario.objects.create_user(
            username="admin",
            password="senha123",
            pessoa=pessoa_admin,
            gerente_comercial=True  # Tem a permissão
        )
        # NÃO adiciona ao grupo Comercial
        
        self.client.login(username="admin", password="senha123")
        
        # Verifica se tem a permissão
        self.assertTrue(usuario_admin.has_perm('core.controle_whatsapp'))
        
        # Mas não pode acessar porque não está no grupo Comercial
        response = self.client.get(reverse('comercial:whatsapp_geral'))
        self.assertEqual(response.status_code, 302)  # Redirect de acesso negado

    def test_usuario_anonimo_nao_pode_acessar(self):
        """Testa se usuário não logado não pode acessar"""
        # Não faz login
        response = self.client.get(reverse('comercial:whatsapp_geral'))
        self.assertEqual(response.status_code, 302)  # Redirect para login

    def test_menu_link_aparece_apenas_para_usuarios_com_permissao(self):
        """Testa se o link no menu aparece apenas para usuários com permissão"""
        # Testa com gerente (tem permissão)
        self.client.login(username="gerente", password="senha123")
        response = self.client.get(reverse('comercial:home'))  # Página que tem o menu
        # Verifica se tem a variável de template perms disponível
        self.assertTrue(response.context['perms']['core']['controle_whatsapp'])
        
        # Testa com atendente (não tem permissão)
        self.client.login(username="atendente", password="senha123")
        response = self.client.get(reverse('comercial:home'))
        self.assertFalse(response.context['perms']['core']['controle_whatsapp'])

    def test_permissao_e_dinamica_ao_alterar_gerente_comercial(self):
        """Testa se a permissão é dinâmica ao alterar o status de gerente comercial"""
        self.client.login(username="atendente", password="senha123")
        
        # Inicialmente não tem acesso
        response = self.client.get(reverse('comercial:whatsapp_geral'))
        self.assertEqual(response.status_code, 302)
        
        # Marca como gerente comercial
        self.usuario_atendente.gerente_comercial = True
        self.usuario_atendente.save()
        
        # Agora deve ter acesso
        response = self.client.get(reverse('comercial:whatsapp_geral'))
        self.assertEqual(response.status_code, 200)