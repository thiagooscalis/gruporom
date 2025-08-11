# -*- coding: utf-8 -*-
"""
Testes para formulário de Usuário com campo Gerente Comercial
"""
from django import forms
from django.test import TestCase
from django.contrib.auth.models import Group
from core.models import Usuario, Pessoa
from core.forms.usuario import UsuarioForm


class GerenteComercialFormTestCase(TestCase):
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

    def test_campo_gerente_comercial_no_form(self):
        """Testa se o campo gerente_comercial está presente no formulário"""
        form = UsuarioForm()
        self.assertIn('gerente_comercial', form.fields)
        # Verifica se é um BooleanField
        self.assertIsInstance(form.fields['gerente_comercial'], forms.BooleanField)

    def test_criacao_usuario_com_gerente_comercial_true(self):
        """Testa criação de usuário marcado como gerente comercial"""
        form_data = {
            'pessoa': self.pessoa.id,
            'pessoa_search': f'{self.pessoa.nome} - {self.pessoa.doc}',
            'username': 'joao',
            'password': 'senha123456',
            'password_confirm': 'senha123456',
            'is_active': True,
            'gerente_comercial': True,
            'groups': [self.grupo_comercial.id],
            'empresas': []
        }
        
        form = UsuarioForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        usuario = form.save()
        self.assertTrue(usuario.gerente_comercial)
        self.assertTrue(usuario.has_perm('core.controle_whatsapp'))

    def test_criacao_usuario_com_gerente_comercial_false(self):
        """Testa criação de usuário NÃO marcado como gerente comercial"""
        form_data = {
            'pessoa': self.pessoa.id,
            'pessoa_search': f'{self.pessoa.nome} - {self.pessoa.doc}',
            'username': 'joao',
            'password': 'senha123456',
            'password_confirm': 'senha123456',
            'is_active': True,
            'gerente_comercial': False,
            'groups': [self.grupo_comercial.id],
            'empresas': []
        }
        
        form = UsuarioForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        usuario = form.save()
        self.assertFalse(usuario.gerente_comercial)
        self.assertFalse(usuario.has_perm('core.controle_whatsapp'))

    def test_edicao_usuario_adicionando_gerente_comercial(self):
        """Testa edição de usuário para adicionar status de gerente comercial"""
        # Cria usuário sem ser gerente
        usuario = Usuario.objects.create_user(
            username="joao",
            password="senha123",
            pessoa=self.pessoa,
            gerente_comercial=False
        )
        usuario.groups.add(self.grupo_comercial)
        
        # Verifica estado inicial
        self.assertFalse(usuario.gerente_comercial)
        self.assertFalse(usuario.has_perm('core.controle_whatsapp'))
        
        # Edita para ser gerente comercial
        form_data = {
            'pessoa': self.pessoa.id,
            'pessoa_search': f'{self.pessoa.nome} - {self.pessoa.doc}',
            'username': 'joao',
            'is_active': True,
            'gerente_comercial': True,  # Mudança aqui
            'groups': [self.grupo_comercial.id],
            'empresas': []
        }
        
        form = UsuarioForm(data=form_data, instance=usuario)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        usuario_editado = form.save()
        self.assertTrue(usuario_editado.gerente_comercial)
        self.assertTrue(usuario_editado.has_perm('core.controle_whatsapp'))

    def test_edicao_usuario_removendo_gerente_comercial(self):
        """Testa edição de usuário para remover status de gerente comercial"""
        # Cria usuário como gerente
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
        
        # Edita para NÃO ser gerente comercial
        form_data = {
            'pessoa': self.pessoa.id,
            'pessoa_search': f'{self.pessoa.nome} - {self.pessoa.doc}',
            'username': 'joao',
            'is_active': True,
            'gerente_comercial': False,  # Mudança aqui
            'groups': [self.grupo_comercial.id],
            'empresas': []
        }
        
        form = UsuarioForm(data=form_data, instance=usuario)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        usuario_editado = form.save()
        self.assertFalse(usuario_editado.gerente_comercial)
        self.assertFalse(usuario_editado.has_perm('core.controle_whatsapp'))