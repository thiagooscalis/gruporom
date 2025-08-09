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
        
        # Campos de email diretos
        self.assertIn('email1', form.fields)
        self.assertIn('email2', form.fields)
        self.assertIn('email3', form.fields)
        
        # Campos de telefone diretos
        self.assertIn('ddi1', form.fields)
        self.assertIn('ddd1', form.fields)
        self.assertIn('telefone1', form.fields)
        self.assertIn('ddi2', form.fields)
        self.assertIn('ddd2', form.fields)
        self.assertIn('telefone2', form.fields)
        self.assertIn('ddi3', form.fields)
        self.assertIn('ddd3', form.fields)
        self.assertIn('telefone3', form.fields)
        
        # Campos de empresa
        self.assertIn('empresa_gruporom', form.fields)
        self.assertIn('tipo_empresa', form.fields)
    
    def test_criar_pessoa_comum(self):
        """Testa criação de pessoa comum (não empresa)"""
        form_data = {
            'nome': 'João Silva',
            'tipo_doc': 'CPF',
            'doc': '11144477735',  # CPF válido
            
            # Campos de email diretos
            'email1': 'joao@teste.com',
            'email2': '',
            'email3': '',
            
            # Campos de telefone diretos
            'ddi1': '55',
            'ddd1': '11',
            'telefone1': '999999999',
            'ddi2': '',
            'ddd2': '',
            'telefone2': '',
            'ddi3': '',
            'ddd3': '',
            'telefone3': '',
            
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
            'doc': '11222333000181',  # CNPJ válido
            
            # Campos de email diretos
            'email1': 'turismo@gruporom.com',
            'email2': '',
            'email3': '',
            
            # Campos de telefone diretos
            'ddi1': '55',
            'ddd1': '11',
            'telefone1': '888888888',
            'ddi2': '',
            'ddd2': '',
            'telefone2': '',
            'ddi3': '',
            'ddd3': '',
            'telefone3': '',
            
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
        from core.factories import PessoaFactory
        pessoa = PessoaFactory(
            nome='Maria Santos',
            tipo_doc='CNPJ',
            doc='11444777000161',  # CNPJ válido
            empresa_gruporom=False
        )
        
        # Editar para empresa
        form_data = {
            'nome': 'Maria Santos Empresa',
            'tipo_doc': 'CNPJ',
            'doc': '11444777000161',  # CNPJ válido
            
            # Campos de email diretos
            'email1': 'maria@gruporom.com',
            'email2': '',
            'email3': '',
            
            # Campos de telefone diretos
            'ddi1': '55',
            'ddd1': '11',
            'telefone1': '777777777',
            'ddi2': '',
            'ddd2': '',
            'telefone2': '',
            'ddi3': '',
            'ddd3': '',
            'telefone3': '',
            
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
        from core.factories import EmpresaGrupoROMFactory
        empresa = EmpresaGrupoROMFactory(
            nome='ROM Administração',
            tipo_doc='CNPJ',
            doc='11222333000181',  # CNPJ válido
            tipo_empresa='Administração de Bens'
        )
        
        # Editar para pessoa comum
        form_data = {
            'nome': 'ROM Administração',
            'tipo_doc': 'CNPJ',
            'doc': '11222333000181',  # CNPJ válido
            
            # Campos de email diretos
            'email1': 'admin@teste.com',
            'email2': '',
            'email3': '',
            
            # Campos de telefone diretos
            'ddi1': '55',
            'ddd1': '11',
            'telefone1': '555555555',
            'ddi2': '',
            'ddd2': '',
            'telefone2': '',
            'ddi3': '',
            'ddd3': '',
            'telefone3': '',
            
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
        from core.factories import EmpresaGrupoROMFactory
        empresa = EmpresaGrupoROMFactory(
            nome='ROM Turismo Original',
            tipo_doc='CNPJ',
            doc='11333444000195',  # CNPJ válido
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
    
    def test_validacao_telefone1_incompleto_da_erro(self):
        """Testa se telefone1 incompleto dá erro (é obrigatório)"""
        # Teste 1: Apenas DDI preenchido no telefone1
        form_data = {
            'nome': 'Teste Telefone',
            'tipo_doc': 'CPF',
            'doc': '11144477735',
            'email1': 'teste@example.com',
            'ddi1': '55',  # Apenas DDI do telefone1
            'ddd1': '',
            'telefone1': '',
            'empresa_gruporom': False,
        }
        
        form = PessoaForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Deve ter erro no telefone1
        self.assertIn('telefone1', form.errors)
        self.assertIn('todos os campos (DDI, DDD e telefone) devem estar preenchidos', str(form.errors['telefone1']))
    
    def test_validacao_telefone2_parcial_e_limpo(self):
        """Testa se campos de telefone2 parcialmente preenchidos são limpos (sem erro)"""
        # Teste: telefone2 com apenas DDI preenchido
        form_data = {
            'nome': 'Teste Telefone',
            'tipo_doc': 'CPF',
            'doc': '11144477735',
            'email1': 'teste@example.com',
            'ddi1': '55',
            'ddd1': '11',
            'telefone1': '999999999',  # Telefone1 completo
            'ddi2': '1',  # Apenas DDI do telefone2
            'ddd2': '',
            'telefone2': '',
            'empresa_gruporom': False,
        }
        
        form = PessoaForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        
        # Telefone2 deve ser limpo porque está incompleto
        cleaned_data = form.cleaned_data
        self.assertEqual(cleaned_data['ddi2'], '')
        self.assertEqual(cleaned_data['ddd2'], '')
        self.assertEqual(cleaned_data['telefone2'], '')
    
    def test_validacao_telefone_campos_completos(self):
        """Testa se campos de telefone completos são mantidos"""
        form_data = {
            'nome': 'Teste Telefone',
            'tipo_doc': 'CPF',
            'doc': '11144477735',
            'email1': 'teste@example.com',
            'ddi1': '55',
            'ddd1': '11',
            'telefone1': '999999999',  # Todos preenchidos
            'empresa_gruporom': False,
        }
        
        form = PessoaForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        
        # Deve manter todos os campos porque está completo
        cleaned_data = form.cleaned_data
        self.assertEqual(cleaned_data['ddi1'], '55')
        self.assertEqual(cleaned_data['ddd1'], '11')
        self.assertEqual(cleaned_data['telefone1'], '999999999')
    
    def test_validacao_telefone_multiplos_campos(self):
        """Testa validação em múltiplos campos de telefone"""
        form_data = {
            'nome': 'Teste Telefone',
            'tipo_doc': 'CPF',
            'doc': '11144477735',
            'email1': 'teste@example.com',
            # Telefone1: completo
            'ddi1': '55',
            'ddd1': '11',
            'telefone1': '999999999',
            # Telefone2: incompleto (só DDI) - deve ser limpo
            'ddi2': '1',
            'ddd2': '',
            'telefone2': '',
            # Telefone3: vazio
            'ddi3': '',
            'ddd3': '',
            'telefone3': '',
            'empresa_gruporom': False,
        }
        
        form = PessoaForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        
        cleaned_data = form.cleaned_data
        # Telefone1: deve manter (completo)
        self.assertEqual(cleaned_data['ddi1'], '55')
        self.assertEqual(cleaned_data['ddd1'], '11')
        self.assertEqual(cleaned_data['telefone1'], '999999999')
        
        # Telefone2: deve limpar (incompleto)
        self.assertIn(cleaned_data['ddi2'], ['', None])
        self.assertIn(cleaned_data['ddd2'], ['', None])
        self.assertIn(cleaned_data['telefone2'], ['', None])
        
        # Telefone3: deve manter vazio
        self.assertIn(cleaned_data['ddi3'], ['', None])
        self.assertIn(cleaned_data['ddd3'], ['', None])
        self.assertIn(cleaned_data['telefone3'], ['', None])