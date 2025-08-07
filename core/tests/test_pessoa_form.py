from django.test import TestCase, override_settings
from django.core.files.storage import InMemoryStorage
from core.forms.pessoa import PessoaForm
from core.choices import TIPO_EMPRESA_CHOICES
from core.models import Pessoa


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class PessoaFormTest(TestCase):
    
    def test_form_fields_presente(self):
        """Testa se todos os campos necessários estão presentes no formulário"""
        form = PessoaForm()
        
        # Campos básicos
        self.assertIn('nome', form.fields)
        self.assertIn('tipo_doc', form.fields)
        self.assertIn('doc', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('telefone', form.fields)
        self.assertIn('empresa_gruporom', form.fields)
        self.assertIn('tipo_empresa', form.fields)
    
    def test_criar_pessoa_comum(self):
        """Testa criação de pessoa comum (não empresa)"""
        form_data = {
            'nome': 'João Silva',
            'tipo_doc': 'CPF',
            'doc': '12345678901',
            'email': 'joao@teste.com',
            'telefone': '11999999999',
            'empresa_gruporom': False,
            'tipo_empresa': '',  # Vazio para pessoa comum
        }
        
        form = PessoaForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        
        pessoa = form.save()
        self.assertFalse(pessoa.empresa_gruporom)
        self.assertIsNone(pessoa.tipo_empresa)
    
    def test_criar_empresa_gruporom(self):
        """Testa criação de empresa do Grupo ROM"""
        form_data = {
            'nome': 'ROM Turismo',
            'tipo_doc': 'CNPJ',
            'doc': '12345678000195',
            'email': 'turismo@gruporom.com',
            'telefone': '11888888888',
            'empresa_gruporom': True,
            'tipo_empresa': 'Turismo',
        }
        
        form = PessoaForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        
        pessoa = form.save()
        self.assertTrue(pessoa.empresa_gruporom)
        self.assertEqual(pessoa.tipo_empresa, 'Turismo')
    
    def test_choices_tipo_empresa_corretas(self):
        """Testa se as choices do campo tipo_empresa estão corretas"""
        form = PessoaForm()
        field_choices = form.fields['tipo_empresa'].choices
        
        # Deve incluir opção vazia + todas as choices definidas
        expected_choices = [('', '---------')] + list(TIPO_EMPRESA_CHOICES)
        self.assertEqual(list(field_choices), expected_choices)
    
    def test_editar_pessoa_para_empresa(self):
        """Testa edição de pessoa comum para empresa do Grupo ROM"""
        # Criar pessoa comum
        pessoa = Pessoa.objects.create(
            nome='Maria Santos',
            tipo_doc='CNPJ',
            doc='98765432000111',
            email='maria@teste.com',
            telefone='11777777777',
            empresa_gruporom=False
        )
        
        # Editar para empresa
        form_data = {
            'nome': 'Maria Santos Empresa',
            'tipo_doc': 'CNPJ',
            'doc': '98765432000111',
            'email': 'maria@gruporom.com',
            'telefone': '11777777777',
            'empresa_gruporom': True,
            'tipo_empresa': 'Alimentação',
        }
        
        form = PessoaForm(data=form_data, instance=pessoa)
        self.assertTrue(form.is_valid(), form.errors)
        
        pessoa_atualizada = form.save()
        self.assertTrue(pessoa_atualizada.empresa_gruporom)
        self.assertEqual(pessoa_atualizada.tipo_empresa, 'Alimentação')
    
    def test_editar_empresa_para_pessoa_comum(self):
        """Testa edição de empresa do Grupo ROM para pessoa comum"""
        # Criar empresa
        empresa = Pessoa.objects.create(
            nome='ROM Administração',
            tipo_doc='CNPJ',
            doc='11111111000122',
            email='admin@gruporom.com',
            telefone='11555555555',
            empresa_gruporom=True,
            tipo_empresa='Administração de Bens'
        )
        
        # Editar para pessoa comum
        form_data = {
            'nome': 'ROM Administração',
            'tipo_doc': 'CNPJ',
            'doc': '11111111000122',
            'email': 'admin@teste.com',
            'telefone': '11555555555',
            'empresa_gruporom': False,
            'tipo_empresa': '',  # Limpar tipo
        }
        
        form = PessoaForm(data=form_data, instance=empresa)
        self.assertTrue(form.is_valid(), form.errors)
        
        pessoa_atualizada = form.save()
        self.assertFalse(pessoa_atualizada.empresa_gruporom)
        # tipo_empresa deve ficar vazio/None quando não é empresa do grupo
        self.assertTrue(pessoa_atualizada.tipo_empresa in ['', None])
    
    def test_form_preserva_dados_na_edicao(self):
        """Testa se o formulário preserva os dados existentes na edição"""
        empresa = Pessoa.objects.create(
            nome='ROM Turismo Original',
            tipo_doc='CNPJ',
            doc='22222222000133',
            email='turismo@gruporom.com',
            telefone='11444444444',
            empresa_gruporom=True,
            tipo_empresa='Turismo'
        )
        
        form = PessoaForm(instance=empresa)
        
        # Verificar se os valores estão pré-preenchidos
        self.assertEqual(form.initial['empresa_gruporom'], True)
        self.assertEqual(form.initial['tipo_empresa'], 'Turismo')
    
    def test_labels_corretos(self):
        """Testa se os labels dos campos estão corretos"""
        form = PessoaForm()
        
        self.assertEqual(form.fields['empresa_gruporom'].label, 'Empresa do Grupo ROM')
        self.assertEqual(form.fields['tipo_empresa'].label, 'Tipo de Empresa')