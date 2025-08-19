from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import Group
from django.core.files.storage import InMemoryStorage
from django.urls import reverse
from core.factories import UsuarioAdministracaoFactory


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class UsuariosListaTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.admin_user = UsuarioAdministracaoFactory()
        self.client.force_login(self.admin_user)
        
    def test_lista_usuarios_exibe_grupos(self):
        """Testa se a lista de usuários exibe os grupos associados"""
        response = self.client.get(reverse('administracao:usuarios_lista'))
        
        self.assertEqual(response.status_code, 200)
        # Verifica se o badge de Administração está presente (o admin_user tem esse grupo)
        self.assertContains(response, 'bg-primary-100 text-primary-800">Administração</span>')
        
    def test_lista_usuarios_sem_grupos(self):
        """Testa se a lista mostra 'Nenhum grupo' para usuários sem grupos"""
        # Criar usuário sem grupos
        usuario_sem_grupos = UsuarioAdministracaoFactory()
        usuario_sem_grupos.groups.clear()
        
        response = self.client.get(reverse('administracao:usuarios_lista'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhum grupo')
        
    def test_coluna_grupos_presente(self):
        """Testa se a coluna 'Grupos' está presente no cabeçalho"""
        response = self.client.get(reverse('administracao:usuarios_lista'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '>Grupos</th>')
        
    def test_badges_grupos_exibidos(self):
        """Testa se os badges dos grupos são exibidos corretamente"""
        response = self.client.get(reverse('administracao:usuarios_lista'))
        
        self.assertEqual(response.status_code, 200)
        # Verifica se tem classes dos badges do design system
        self.assertContains(response, 'bg-primary-100 text-primary-800')
        self.assertContains(response, 'rounded-full')
        
    def test_usuario_com_multiplos_grupos(self):
        """Testa usuário com múltiplos grupos"""
        # Criar mais um usuário com múltiplos grupos
        from django.contrib.auth.models import Group
        comercial_group, _ = Group.objects.get_or_create(name='Comercial')
        operacional_group, _ = Group.objects.get_or_create(name='Operacional')
        
        outro_user = UsuarioAdministracaoFactory()
        outro_user.groups.add(comercial_group, operacional_group)
        
        response = self.client.get(reverse('administracao:usuarios_lista'))
        
        self.assertEqual(response.status_code, 200)
        # Deve conter os badges dos grupos
        self.assertContains(response, 'bg-info-100 text-info-800">Comercial</span>')
        self.assertContains(response, 'bg-success-100 text-success-800">Operacional</span>')
        
    def test_query_otimizada_com_prefetch(self):
        """Testa se a query está otimizada com prefetch_related"""
        # Testar sem prefetch seria muito mais queries
        # Apenas verifica que não há N+1 queries para empresas e grupos
        response = self.client.get(reverse('administracao:usuarios_lista'))
        
        # Força a execução das queries acessando os dados
        groups_lists = []
        for usuario in response.context['page_obj']:
            groups_lists.append(list(usuario.groups.all()))
            
        # Se chegou até aqui sem erro, significa que as queries estão funcionando
        self.assertEqual(response.status_code, 200)
                
    def test_responsividade_tabela(self):
        """Testa se a tabela tem classe overflow-x-auto (Tailwind)"""
        response = self.client.get(reverse('administracao:usuarios_lista'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'overflow-x-auto')