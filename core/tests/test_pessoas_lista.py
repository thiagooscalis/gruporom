from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import Group
from django.core.files.storage import InMemoryStorage
from django.urls import reverse
from core.factories import UsuarioAdministracaoFactory, PessoaFactory, PessoaJuridicaFactory, EmpresaGrupoROMFactory
from core.models import Pessoa


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class PessoasListaTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.admin_user = UsuarioAdministracaoFactory()
        self.client.force_login(self.admin_user)
        
        # Criar pessoas de teste
        self.pessoa_fisica = PessoaFactory(nome='João Silva', tipo_doc='CPF')
        self.pessoa_juridica = PessoaJuridicaFactory(nome='Empresa ABC', tipo_doc='CNPJ')
        self.empresa_gruporom = EmpresaGrupoROMFactory(nome='ROM Turismo', tipo_empresa='Turismo')
        
    def test_lista_pessoas_exibe_badges_corretos(self):
        """Testa se a lista exibe os badges corretos (PF, PJ, Grupo ROM)"""
        response = self.client.get(reverse('administracao:pessoas_lista'))
        
        self.assertEqual(response.status_code, 200)
        # Verifica badges
        self.assertContains(response, 'badge bg-info">PF</span>')
        self.assertContains(response, 'badge bg-success">PJ</span>')
        self.assertContains(response, 'badge bg-warning text-dark">Grupo ROM</span>')
        
    def test_filtro_pessoa_fisica(self):
        """Testa filtro de Pessoa Física"""
        response = self.client.get(reverse('administracao:pessoas_lista'), {'tipo': 'pf'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'João Silva')
        self.assertNotContains(response, 'Empresa ABC')
        self.assertNotContains(response, 'ROM Turismo')
        
    def test_filtro_pessoa_juridica(self):
        """Testa filtro de Pessoa Jurídica"""
        response = self.client.get(reverse('administracao:pessoas_lista'), {'tipo': 'pj'})
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'João Silva')
        self.assertContains(response, 'Empresa ABC')
        # Empresa Grupo ROM não deve aparecer pois é filtro específico
        self.assertNotContains(response, 'ROM Turismo')
        
    def test_filtro_grupo_rom(self):
        """Testa filtro de Empresa Grupo ROM"""
        response = self.client.get(reverse('administracao:pessoas_lista'), {'tipo': 'gruporom'})
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'João Silva')
        self.assertNotContains(response, 'Empresa ABC')
        self.assertContains(response, 'ROM Turismo')
        
    def test_filtro_todos(self):
        """Testa sem filtro (todos os tipos)"""
        response = self.client.get(reverse('administracao:pessoas_lista'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'João Silva')
        self.assertContains(response, 'Empresa ABC')
        self.assertContains(response, 'ROM Turismo')
        
    def test_busca_com_filtro(self):
        """Testa busca combinada com filtro"""
        response = self.client.get(reverse('administracao:pessoas_lista'), {
            'search': 'ROM',
            'tipo': 'gruporom'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ROM Turismo')
        self.assertNotContains(response, 'João Silva')
        self.assertNotContains(response, 'Empresa ABC')
        
    def test_paginacao_preserva_filtro(self):
        """Testa se a paginação preserva o filtro selecionado"""
        # Criar mais pessoas para ter paginação
        for i in range(25):
            PessoaFactory(nome=f'Pessoa {i}', tipo_doc='CPF')
        
        response = self.client.get(reverse('administracao:pessoas_lista'), {'tipo': 'pf'})
        
        self.assertEqual(response.status_code, 200)
        # Verifica se o link de paginação contém o filtro
        self.assertContains(response, '&tipo=pf')
        
    def test_select_filtro_mantem_selecao(self):
        """Testa se o select mantém a opção selecionada"""
        response = self.client.get(reverse('administracao:pessoas_lista'), {'tipo': 'pf'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<option value="pf" selected>Pessoa Física</option>')
        
    def test_select_filtro_opcoes_corretas(self):
        """Testa se o select tem todas as opções corretas"""
        response = self.client.get(reverse('administracao:pessoas_lista'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<option value="">Todos os Tipos</option>')
        self.assertContains(response, '<option value="pf"')
        self.assertContains(response, '>Pessoa Física</option>')
        self.assertContains(response, '<option value="pj"')
        self.assertContains(response, '>Pessoa Jurídica</option>')
        self.assertContains(response, '<option value="gruporom"')
        self.assertContains(response, '>Empresa Grupo ROM</option>')
        
    def test_badge_grupo_rom_prioridade(self):
        """Testa se empresas do Grupo ROM mostram badge Grupo ROM mesmo sendo PJ"""
        response = self.client.get(reverse('administracao:pessoas_lista'))
        
        self.assertEqual(response.status_code, 200)
        # A empresa do Grupo ROM deve mostrar badge "Grupo ROM" e não "PJ"
        content = str(response.content)
        rom_index = content.find('ROM Turismo')
        self.assertGreater(rom_index, 0, "ROM Turismo não encontrado")
        
        # Procurar pelo badge após o nome
        badge_section = content[rom_index:rom_index+500]
        self.assertIn('Grupo ROM', badge_section)
        self.assertNotIn('>PJ<', badge_section)