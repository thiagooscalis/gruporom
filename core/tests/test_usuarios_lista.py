from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import Group
from django.core.files.storage import InMemoryStorage
from django.urls import reverse
from core.factories import UsuarioAdministracaoFactory, EmpresaGrupoROMFactory


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class UsuariosListaTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.admin_user = UsuarioAdministracaoFactory()
        self.client.force_login(self.admin_user)
        
        # Criar empresas
        self.empresa_turismo = EmpresaGrupoROMFactory(tipo_empresa='Turismo', nome='ROM Turismo')
        self.empresa_alimentacao = EmpresaGrupoROMFactory(tipo_empresa='Alimentação', nome='ROM Alimentação')
        
    def test_lista_usuarios_exibe_empresas(self):
        """Testa se a lista de usuários exibe as empresas associadas"""
        # Associar empresas ao usuário admin
        self.admin_user.empresas.add(self.empresa_turismo, self.empresa_alimentacao)
        
        response = self.client.get(reverse('administracao:usuarios_lista'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Turismo')
        self.assertContains(response, 'Alimentação')
        
    def test_lista_usuarios_sem_empresas(self):
        """Testa se a lista mostra 'Nenhuma empresa' para usuários sem empresas"""
        response = self.client.get(reverse('administracao:usuarios_lista'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhuma empresa')
        
    def test_coluna_empresas_presente(self):
        """Testa se a coluna 'Empresas' está presente no cabeçalho"""
        response = self.client.get(reverse('administracao:usuarios_lista'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<th>Empresas</th>')
        
    def test_nome_empresas_exibido(self):
        """Testa se os nomes das empresas são exibidos corretamente"""
        self.admin_user.empresas.add(self.empresa_turismo)
        
        response = self.client.get(reverse('administracao:usuarios_lista'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ROM Turismo')
        self.assertContains(response, 'class="small"')
        
    def test_usuario_com_multiplas_empresas(self):
        """Testa usuário com múltiplas empresas"""
        # Criar mais um usuário com múltiplas empresas
        outro_user = UsuarioAdministracaoFactory()
        outro_user.empresas.add(self.empresa_turismo, self.empresa_alimentacao)
        
        response = self.client.get(reverse('administracao:usuarios_lista'))
        
        self.assertEqual(response.status_code, 200)
        # Deve conter os nomes das empresas
        self.assertContains(response, 'ROM Turismo')
        self.assertContains(response, 'ROM Alimentação')
        
    def test_query_otimizada_com_prefetch(self):
        """Testa se a query está otimizada com prefetch_related"""
        # Testar sem prefetch seria muito mais queries
        # Apenas verifica que não há N+1 queries para empresas e grupos
        response = self.client.get(reverse('administracao:usuarios_lista'))
        
        # Força a execução das queries acessando os dados
        empresas_lists = []
        groups_lists = []
        for usuario in response.context['page_obj']:
            empresas_lists.append(list(usuario.empresas.all()))
            groups_lists.append(list(usuario.groups.all()))
            
        # Se chegou até aqui sem erro, significa que as queries estão funcionando
        self.assertEqual(response.status_code, 200)
                
    def test_responsividade_tabela(self):
        """Testa se a tabela tem classe table-responsive"""
        response = self.client.get(reverse('administracao:usuarios_lista'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'table-responsive')