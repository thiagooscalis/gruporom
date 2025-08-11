# -*- coding: utf-8 -*-
"""
Testes para verificar remoção de permissões ao desmarcar gerente comercial no formulário
"""
from django import forms
from django.test import TestCase
from django.contrib.auth.models import Group
from core.models import Usuario, Pessoa
from core.forms.usuario import UsuarioForm


class FormGerenteComercialUncheckedTestCase(TestCase):
    def setUp(self):
        """Configura dados para os testes"""
        # Cria uma pessoa
        self.pessoa = Pessoa.objects.create(
            nome="João Silva",
            tipo_doc="cpf",
            doc="12345678901"
        )
        
        # Cria um grupo para os testes
        self.grupo_comercial = Group.objects.create(name='Comercial')

    def test_edicao_usuario_desmarcando_gerente_comercial_via_form(self):
        """Testa se ao desmarcar gerente comercial via form as permissões são removidas"""
        # Cria usuário como gerente comercial
        usuario = Usuario.objects.create_user(
            username="joao",
            password="senha123",
            pessoa=self.pessoa,
            gerente_comercial=True  # Criado como gerente
        )
        usuario.groups.add(self.grupo_comercial)
        
        # Verifica estado inicial
        self.assertTrue(usuario.gerente_comercial)
        self.assertTrue(usuario.has_perm('core.controle_whatsapp'))
        
        # Edita via form DESMARCANDO gerente comercial
        form_data = {
            'pessoa': self.pessoa.id,
            'pessoa_search': f'{self.pessoa.nome} - {self.pessoa.doc}',
            'username': 'joao',
            'is_active': True,
            'gerente_comercial': False,  # DESMARCADO
            'groups': [self.grupo_comercial.id],
            'empresas': []
        }
        
        form = UsuarioForm(data=form_data, instance=usuario)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        # Salva o formulário
        usuario_editado = form.save()
        
        # Recarrega da base de dados para ter certeza
        usuario_editado.refresh_from_db()
        
        # Verifica se foi desmarcado e se perdeu a permissão
        self.assertFalse(usuario_editado.gerente_comercial)
        self.assertFalse(usuario_editado.has_perm('core.controle_whatsapp'))

    def test_criacao_usuario_sem_gerente_comercial_via_form(self):
        """Testa criação de usuário sem marcar gerente comercial"""
        form_data = {
            'pessoa': self.pessoa.id,
            'pessoa_search': f'{self.pessoa.nome} - {self.pessoa.doc}',
            'username': 'joao',
            'password': 'senha123456',
            'password_confirm': 'senha123456',
            'is_active': True,
            'gerente_comercial': False,  # NÃO MARCADO
            'groups': [self.grupo_comercial.id],
            'empresas': []
        }
        
        form = UsuarioForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        usuario = form.save()
        
        # Verifica se não tem permissão
        self.assertFalse(usuario.gerente_comercial)
        self.assertFalse(usuario.has_perm('core.controle_whatsapp'))

    def test_edicao_usuario_sem_alterar_gerente_comercial_mantem_permissoes(self):
        """Testa se ao editar sem alterar o campo gerente_comercial as permissões são mantidas"""
        # Cria usuário como gerente comercial
        usuario = Usuario.objects.create_user(
            username="joao",
            password="senha123",
            pessoa=self.pessoa,
            gerente_comercial=True
        )
        usuario.groups.add(self.grupo_comercial)
        
        # Verifica estado inicial
        self.assertTrue(usuario.gerente_comercial)
        self.assertTrue(usuario.has_perm('core.controle_whatsapp'))
        
        # Edita via form MANTENDO gerente comercial marcado
        form_data = {
            'pessoa': self.pessoa.id,
            'pessoa_search': f'{self.pessoa.nome} - {self.pessoa.doc}',
            'username': 'joao_novo',  # Muda apenas o username
            'is_active': True,
            'gerente_comercial': True,  # MANTÉM MARCADO
            'groups': [self.grupo_comercial.id],
            'empresas': []
        }
        
        form = UsuarioForm(data=form_data, instance=usuario)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        usuario_editado = form.save()
        
        # Verifica se mantém a permissão
        self.assertTrue(usuario_editado.gerente_comercial)
        self.assertTrue(usuario_editado.has_perm('core.controle_whatsapp'))
        self.assertEqual(usuario_editado.username, 'joao_novo')

    def test_campo_gerente_comercial_false_por_padrao_no_form(self):
        """Testa se o campo gerente_comercial é False por padrão no form"""
        form = UsuarioForm()
        
        # Verifica se o campo existe
        self.assertIn('gerente_comercial', form.fields)
        
        # Para um formulário vazio, o valor inicial deve ser False
        # (BooleanField não marcado = False)
        form_data = {
            'pessoa': self.pessoa.id,
            'pessoa_search': f'{self.pessoa.nome} - {self.pessoa.doc}',
            'username': 'teste',
            'password': 'senha123456',
            'password_confirm': 'senha123456',
            'is_active': True,
            # gerente_comercial omitido (= False)
            'groups': [self.grupo_comercial.id],
            'empresas': []
        }
        
        form = UsuarioForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        usuario = form.save()
        self.assertFalse(usuario.gerente_comercial)