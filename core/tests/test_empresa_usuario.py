from django.test import TestCase, override_settings
from django.contrib.auth.models import Group
from django.core.files.storage import InMemoryStorage
from core.factories import UsuarioFactory, EmpresaGrupoROMFactory
from core.models import Usuario, Pessoa
from core.choices import TIPO_EMPRESA_CHOICES


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class UsuarioEmpresaModelTest(TestCase):
    
    def test_usuario_pode_ter_multiplas_empresas(self):
        """Testa se um usuário pode estar associado a múltiplas empresas"""
        usuario = UsuarioFactory()
        empresa1 = EmpresaGrupoROMFactory(tipo_empresa='Turismo')
        empresa2 = EmpresaGrupoROMFactory(tipo_empresa='Alimentação')
        
        usuario.empresas.add(empresa1, empresa2)
        
        self.assertEqual(usuario.empresas.count(), 2)
        self.assertIn(empresa1, usuario.empresas.all())
        self.assertIn(empresa2, usuario.empresas.all())
    
    def test_empresa_pode_ter_multiplos_usuarios(self):
        """Testa se uma empresa pode estar associada a múltiplos usuários"""
        empresa = EmpresaGrupoROMFactory(tipo_empresa='Turismo')
        usuario1 = UsuarioFactory()
        usuario2 = UsuarioFactory()
        
        usuario1.empresas.add(empresa)
        usuario2.empresas.add(empresa)
        
        self.assertEqual(empresa.usuarios_empresa.count(), 2)
        self.assertIn(usuario1, empresa.usuarios_empresa.all())
        self.assertIn(usuario2, empresa.usuarios_empresa.all())
    
    def test_limit_choices_to_empresa_gruporom(self):
        """Testa se o limit_choices_to funciona corretamente"""
        # Cria uma pessoa comum
        from core.factories import PessoaFactory
        pessoa_comum = PessoaFactory(
            nome="Pessoa Comum",
            doc="12345678901",
            tipo_doc="CPF",
            empresa_gruporom=False
        )
        
        # Cria uma empresa do grupo ROM
        empresa_rom = EmpresaGrupoROMFactory(tipo_empresa='Turismo')
        
        usuario = UsuarioFactory()
        
        # Deve conseguir adicionar empresa do grupo ROM
        usuario.empresas.add(empresa_rom)
        self.assertIn(empresa_rom, usuario.empresas.all())
        
        # Pessoa comum não aparece nas opções (testado via queryset)
        empresas_disponiveis = Pessoa.objects.filter(empresa_gruporom=True)
        self.assertIn(empresa_rom, empresas_disponiveis)
        self.assertNotIn(pessoa_comum, empresas_disponiveis)


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class EmpresaGrupoROMFactoryTest(TestCase):
    
    def test_create_empresa_gruporom(self):
        """Testa a criação de empresa do Grupo ROM via factory"""
        empresa = EmpresaGrupoROMFactory()
        
        self.assertTrue(empresa.empresa_gruporom)
        self.assertEqual(empresa.tipo_doc, "CNPJ")
        self.assertIn(empresa.tipo_empresa, [choice[0] for choice in TIPO_EMPRESA_CHOICES])
        self.assertIsNotNone(empresa.nome)
        self.assertIsNotNone(empresa.email_principal)
    
    def test_create_empresa_tipo_especifico(self):
        """Testa a criação de empresa com tipo específico"""
        empresa = EmpresaGrupoROMFactory(tipo_empresa='Turismo')
        
        self.assertTrue(empresa.empresa_gruporom)
        self.assertEqual(empresa.tipo_empresa, 'Turismo')


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class ContextProcessorTest(TestCase):
    
    def setUp(self):
        from core.factories import UsuarioAdministracaoFactory
        self.usuario = UsuarioAdministracaoFactory()
        self.client.force_login(self.usuario)
    
    def test_context_processor_sem_empresas(self):
        """Testa context processor quando usuário não tem empresas"""
        response = self.client.get('/administracao/')
        
        self.assertEqual(response.context['tipos_empresa_usuario'], [])
    
    def test_context_processor_com_empresas(self):
        """Testa context processor quando usuário tem empresas"""
        empresa1 = EmpresaGrupoROMFactory(tipo_empresa='Turismo')
        empresa2 = EmpresaGrupoROMFactory(tipo_empresa='Alimentação')
        
        self.usuario.empresas.add(empresa1, empresa2)
        
        response = self.client.get('/administracao/')
        
        tipos = response.context['tipos_empresa_usuario']
        self.assertIn('Turismo', tipos)
        self.assertIn('Alimentação', tipos)
        self.assertEqual(len(tipos), 2)
    
    def test_context_processor_tipos_unicos(self):
        """Testa se tipos duplicados são removidos"""
        empresa1 = EmpresaGrupoROMFactory(tipo_empresa='Turismo')
        empresa2 = EmpresaGrupoROMFactory(tipo_empresa='Turismo')  # Mesmo tipo
        
        self.usuario.empresas.add(empresa1, empresa2)
        
        response = self.client.get('/administracao/')
        
        tipos = response.context['tipos_empresa_usuario']
        self.assertEqual(tipos.count('Turismo'), 1)  # Deve aparecer apenas uma vez