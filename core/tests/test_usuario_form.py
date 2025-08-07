from django.test import TestCase, override_settings
from django.contrib.auth.models import Group
from django.core.files.storage import InMemoryStorage
from core.forms import UsuarioForm
from core.factories import PessoaFactory, EmpresaGrupoROMFactory
from core.models import Usuario


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class UsuarioFormTest(TestCase):
    
    def setUp(self):
        # Criar grupos necessários
        self.admin_group = Group.objects.create(name="Administração")
        
        # Criar empresas do Grupo ROM
        self.empresa_turismo = EmpresaGrupoROMFactory(tipo_empresa='Turismo')
        self.empresa_alimentacao = EmpresaGrupoROMFactory(tipo_empresa='Alimentação')
        
        # Criar pessoa para associar ao usuário
        self.pessoa = PessoaFactory()
    
    def test_form_fields_presente(self):
        """Testa se todos os campos necessários estão presentes no formulário"""
        form = UsuarioForm()
        
        # Campos básicos
        self.assertIn('pessoa', form.fields)
        self.assertIn('pessoa_search', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('is_active', form.fields)
        self.assertIn('groups', form.fields)
        self.assertIn('empresas', form.fields)
        self.assertIn('password', form.fields)
        self.assertIn('password_confirm', form.fields)
    
    def test_empresas_queryset_correto(self):
        """Testa se o queryset de empresas está correto"""
        form = UsuarioForm()
        
        # Deve mostrar apenas empresas do Grupo ROM
        empresas_queryset = form.fields['empresas'].queryset
        self.assertEqual(empresas_queryset.count(), 2)
        self.assertIn(self.empresa_turismo, empresas_queryset)
        self.assertIn(self.empresa_alimentacao, empresas_queryset)
    
    def test_criar_usuario_com_empresas(self):
        """Testa criação de usuário com empresas selecionadas"""
        form_data = {
            'pessoa': self.pessoa.pk,
            'username': 'teste_usuario',
            'is_active': True,
            'groups': [self.admin_group.pk],
            'empresas': [self.empresa_turismo.pk, self.empresa_alimentacao.pk],
            'password': 'senha12345',
            'password_confirm': 'senha12345'
        }
        
        form = UsuarioForm(data=form_data)
        form.fields['pessoa'].queryset = form.fields['pessoa'].queryset.model.objects.filter(pk=self.pessoa.pk)
        
        self.assertTrue(form.is_valid(), form.errors)
        
        usuario = form.save()
        
        # Verificar se as empresas foram associadas
        self.assertEqual(usuario.empresas.count(), 2)
        self.assertIn(self.empresa_turismo, usuario.empresas.all())
        self.assertIn(self.empresa_alimentacao, usuario.empresas.all())
    
    def test_criar_usuario_sem_empresas(self):
        """Testa criação de usuário sem empresas selecionadas"""
        form_data = {
            'pessoa': self.pessoa.pk,
            'username': 'teste_usuario2',
            'is_active': True,
            'groups': [self.admin_group.pk],
            'empresas': [],  # Nenhuma empresa
            'password': 'senha12345',
            'password_confirm': 'senha12345'
        }
        
        form = UsuarioForm(data=form_data)
        form.fields['pessoa'].queryset = form.fields['pessoa'].queryset.model.objects.filter(pk=self.pessoa.pk)
        
        self.assertTrue(form.is_valid(), form.errors)
        
        usuario = form.save()
        
        # Verificar se nenhuma empresa foi associada
        self.assertEqual(usuario.empresas.count(), 0)
    
    def test_editar_usuario_alterando_empresas(self):
        """Testa edição de usuário alterando empresas"""
        # Criar usuário inicial com uma empresa
        usuario = Usuario.objects.create(
            pessoa=self.pessoa,
            username='teste_edit',
            is_active=True
        )
        usuario.set_password('senha123')
        usuario.save()
        usuario.groups.add(self.admin_group)
        usuario.empresas.add(self.empresa_turismo)
        
        # Editar para incluir outra empresa
        form_data = {
            'pessoa': self.pessoa.pk,
            'username': 'teste_edit',
            'is_active': True,
            'groups': [self.admin_group.pk],
            'empresas': [self.empresa_turismo.pk, self.empresa_alimentacao.pk],
            'password': '',  # Sem alterar senha
            'password_confirm': ''
        }
        
        form = UsuarioForm(data=form_data, instance=usuario)
        form.fields['pessoa'].queryset = form.fields['pessoa'].queryset.model.objects.filter(pk=self.pessoa.pk)
        
        self.assertTrue(form.is_valid(), form.errors)
        
        usuario_atualizado = form.save()
        
        # Verificar se ambas as empresas estão associadas
        self.assertEqual(usuario_atualizado.empresas.count(), 2)
        self.assertIn(self.empresa_turismo, usuario_atualizado.empresas.all())
        self.assertIn(self.empresa_alimentacao, usuario_atualizado.empresas.all())
    
    def test_empresas_field_opcional(self):
        """Testa se o campo empresas é opcional"""
        form = UsuarioForm()
        self.assertFalse(form.fields['empresas'].required)
    
    def test_empresas_field_help_text(self):
        """Testa se o help text do campo empresas está correto"""
        form = UsuarioForm()
        expected_help_text = "Selecione as empresas que o usuário pode acessar"
        self.assertEqual(form.fields['empresas'].help_text, expected_help_text)
    
    def test_form_preserva_empresas_na_edicao(self):
        """Testa se o formulário preserva as empresas selecionadas na edição"""
        # Criar usuário com empresas
        usuario = Usuario.objects.create(
            pessoa=self.pessoa,
            username='teste_preserva',
            is_active=True
        )
        usuario.set_password('senha123')
        usuario.save()
        usuario.groups.add(self.admin_group)
        usuario.empresas.add(self.empresa_turismo, self.empresa_alimentacao)
        
        # Criar formulário para edição
        form = UsuarioForm(instance=usuario)
        
        # Verificar se as empresas estão pré-selecionadas
        empresas_selecionadas = form.initial.get('empresas', [])
        self.assertIn(self.empresa_turismo, empresas_selecionadas)
        self.assertIn(self.empresa_alimentacao, empresas_selecionadas)