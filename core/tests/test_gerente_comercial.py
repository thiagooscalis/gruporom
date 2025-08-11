# -*- coding: utf-8 -*-
"""
Testes para funcionalidade de Gerente Comercial
"""
from django.test import TestCase
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Usuario, Pessoa


class GerenteComercialTestCase(TestCase):
    def setUp(self):
        """Configura dados para os testes"""
        # Cria uma pessoa
        self.pessoa = Pessoa.objects.create(
            nome="João Silva",
            tipo_doc="cpf",
            doc="12345678901"
        )
        
        # Cria um usuário
        self.usuario = Usuario.objects.create_user(
            username="joao",
            password="senha123",
            pessoa=self.pessoa
        )

    def test_campo_gerente_comercial_padrao_false(self):
        """Testa se o campo gerente_comercial tem valor padrão False"""
        self.assertFalse(self.usuario.gerente_comercial)

    def test_criacao_permissao_controle_whatsapp(self):
        """Testa se a permissão controle_whatsapp é criada automaticamente"""
        # Marca como gerente comercial
        self.usuario.gerente_comercial = True
        self.usuario.save()
        
        # Verifica se a permissão foi criada
        permission_exists = Permission.objects.filter(
            codename='controle_whatsapp'
        ).exists()
        self.assertTrue(permission_exists)
        
        # Verifica se a permissão tem o nome correto
        permission = Permission.objects.get(codename='controle_whatsapp')
        self.assertEqual(permission.name, 'Pode gerenciar WhatsApp Business')
        
        # Verifica se está associada ao content_type correto
        content_type = ContentType.objects.get_for_model(Usuario)
        self.assertEqual(permission.content_type, content_type)

    def test_atribuicao_permissao_ao_marcar_gerente(self):
        """Testa se a permissão é atribuída ao marcar como gerente comercial"""
        # Marca como gerente comercial
        self.usuario.gerente_comercial = True
        self.usuario.save()
        
        # Verifica se o usuário tem a permissão
        self.assertTrue(self.usuario.has_perm('core.controle_whatsapp'))
        
        # Verifica se a permissão está nas user_permissions
        permission = Permission.objects.get(codename='controle_whatsapp')
        self.assertIn(permission, self.usuario.user_permissions.all())

    def test_remocao_permissao_ao_desmarcar_gerente(self):
        """Testa se a permissão é removida ao desmarcar gerente comercial"""
        # Primeiro marca como gerente comercial
        self.usuario.gerente_comercial = True
        self.usuario.save()
        
        # Verifica que tem a permissão
        self.assertTrue(self.usuario.has_perm('core.controle_whatsapp'))
        
        # Desmarca como gerente comercial
        self.usuario.gerente_comercial = False
        self.usuario.save()
        
        # Verifica se a permissão foi removida
        self.assertFalse(self.usuario.has_perm('core.controle_whatsapp'))
        
        # Verifica se não está mais nas user_permissions
        permission = Permission.objects.get(codename='controle_whatsapp')
        self.assertNotIn(permission, self.usuario.user_permissions.all())

    def test_nao_altera_permissoes_se_campo_nao_mudou(self):
        """Testa se as permissões não são alteradas se o campo não mudou"""
        # Marca como gerente comercial
        self.usuario.gerente_comercial = True
        self.usuario.save()
        
        # Pega a quantidade inicial de permissões
        initial_permissions_count = self.usuario.user_permissions.count()
        
        # Salva novamente sem alterar o campo
        self.usuario.save()
        
        # Verifica que a quantidade de permissões não mudou
        final_permissions_count = self.usuario.user_permissions.count()
        self.assertEqual(initial_permissions_count, final_permissions_count)

    def test_permissao_mantem_entre_criacao_e_edicao(self):
        """Testa se a permissão é mantida em edições do usuário"""
        # Marca como gerente comercial na criação
        self.usuario.gerente_comercial = True
        self.usuario.save()
        
        # Verifica que tem a permissão
        self.assertTrue(self.usuario.has_perm('core.controle_whatsapp'))
        
        # Faz uma edição que não altera o campo gerente_comercial
        self.usuario.username = "joao_silva"
        self.usuario.save()
        
        # Verifica que ainda tem a permissão
        self.assertTrue(self.usuario.has_perm('core.controle_whatsapp'))

    def test_novo_usuario_criado_como_gerente(self):
        """Testa criação de usuário já marcado como gerente comercial"""
        # Cria nova pessoa
        pessoa2 = Pessoa.objects.create(
            nome="Maria Santos",
            tipo_doc="cpf", 
            doc="98765432100"
        )
        
        # Cria usuário já como gerente comercial
        usuario2 = Usuario.objects.create_user(
            username="maria",
            password="senha123",
            pessoa=pessoa2,
            gerente_comercial=True
        )
        
        # Verifica se tem a permissão
        self.assertTrue(usuario2.has_perm('core.controle_whatsapp'))