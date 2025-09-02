# -*- coding: utf-8 -*-
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import Group
from django.core.files.storage import InMemoryStorage
from django.urls import reverse
from core.factories import (
    UsuarioFactory, GroupFactory, CaravanaFactory, 
    BloqueioFactory, PassageiroFactory, PessoaFactory
)
from core.models import Usuario


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class ComercialBaseViewsTest(TestCase):
    
    def setUp(self):
        """Configura dados para os testes"""
        self.client = Client()
        
        # Criar grupo comercial
        self.grupo_comercial = GroupFactory(name='Comercial')
        
        # Criar usuário comercial
        self.user_comercial = UsuarioFactory()
        self.user_comercial.groups.add(self.grupo_comercial)
        
        # Criar usuário sem grupo comercial para testes de permissão
        self.user_sem_permissao = UsuarioFactory()
        
        # Fazer login do usuário comercial
        self.client.force_login(self.user_comercial)
    
    def test_home_comercial_acesso_autorizado(self):
        """Testa se usuário comercial pode acessar a home"""
        response = self.client.get(reverse('comercial:home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Área Comercial')
        self.assertEqual(response.context['title'], 'Área Comercial')
    
    def test_home_comercial_acesso_negado_sem_grupo(self):
        """Testa se usuário sem grupo comercial é negado"""
        self.client.force_login(self.user_sem_permissao)
        response = self.client.get(reverse('comercial:home'))
        
        # Usuário deve ser redirecionado para login ou receber 403
        self.assertIn(response.status_code, [302, 403])
    
    def test_nova_venda_acesso_autorizado(self):
        """Testa se usuário comercial pode acessar nova venda"""
        response = self.client.get(reverse('comercial:nova_venda'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nova Venda')
        self.assertEqual(response.context['title'], 'Nova Venda')
    
    def test_nova_venda_acesso_negado_sem_grupo(self):
        """Testa se usuário sem grupo comercial é negado em nova venda"""
        self.client.force_login(self.user_sem_permissao)
        response = self.client.get(reverse('comercial:nova_venda'))
        
        # Usuário deve ser redirecionado para login ou receber 403
        self.assertIn(response.status_code, [302, 403])
    
    def test_caravanas_disponiveis_sem_caravanas(self):
        """Testa listagem de caravanas quando não há caravanas"""
        response = self.client.get(reverse('comercial:caravanas_disponiveis'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Caravanas Disponíveis')
        self.assertEqual(response.context['title'], 'Caravanas Disponíveis')
        self.assertEqual(len(response.context['caravanas']), 0)
    
    def test_caravanas_disponiveis_com_caravanas(self):
        """Testa listagem de caravanas com dados"""
        # Criar caravana
        caravana = CaravanaFactory(quantidade=10)
        
        response = self.client.get(reverse('comercial:caravanas_disponiveis'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['caravanas']), 1)
        
        # Verificar se cálculo de disponíveis está correto
        caravana_context = response.context['caravanas'][0]
        self.assertEqual(caravana_context.total_passageiros_vendidos, 0)
        self.assertEqual(caravana_context.passageiros_disponiveis, 10)
    
    def test_caravanas_disponiveis_com_passageiros_vendidos(self):
        """Testa cálculo de disponíveis com passageiros já vendidos"""
        # Criar caravana com 10 vagas
        caravana = CaravanaFactory(quantidade=10)
        
        # Criar bloqueio para a caravana
        bloqueio = BloqueioFactory(caravana=caravana)
        
        # Criar 3 passageiros vendidos
        for _ in range(3):
            PassageiroFactory(bloqueio=bloqueio)
        
        response = self.client.get(reverse('comercial:caravanas_disponiveis'))
        
        self.assertEqual(response.status_code, 200)
        caravana_context = response.context['caravanas'][0]
        self.assertEqual(caravana_context.total_passageiros_vendidos, 3)
        self.assertEqual(caravana_context.passageiros_disponiveis, 7)
    
    def test_caravana_detalhes_existente(self):
        """Testa visualização de detalhes de caravana existente"""
        caravana = CaravanaFactory(quantidade=5, nome='Caravana Teste')
        
        response = self.client.get(
            reverse('comercial:caravana_detalhes', kwargs={'caravana_id': caravana.id})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['title'], 'Detalhes - Caravana Teste')
        self.assertEqual(response.context['caravana'], caravana)
        self.assertEqual(response.context['passageiros_disponiveis'], 5)
        self.assertEqual(response.context['total_passageiros_vendidos'], 0)
    
    def test_caravana_detalhes_com_bloqueios(self):
        """Testa detalhes da caravana com bloqueios associados"""
        caravana = CaravanaFactory()
        
        # Criar bloqueios ativos e inativos para a caravana
        bloqueio_ativo = BloqueioFactory(caravana=caravana, ativo=True)
        bloqueio_inativo = BloqueioFactory(caravana=caravana, ativo=False)
        
        response = self.client.get(
            reverse('comercial:caravana_detalhes', kwargs={'caravana_id': caravana.id})
        )
        
        self.assertEqual(response.status_code, 200)
        # Deve retornar apenas bloqueios ativos
        self.assertEqual(len(response.context['bloqueios']), 1)
        self.assertEqual(response.context['bloqueios'][0], bloqueio_ativo)
    
    def test_caravana_detalhes_inexistente(self):
        """Testa acesso a caravana que não existe"""
        response = self.client.get(
            reverse('comercial:caravana_detalhes', kwargs={'caravana_id': 99999})
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_quantidade_range_calculation(self):
        """Testa cálculo do range de quantidades disponíveis"""
        # Caravana com 3 vagas disponíveis
        caravana = CaravanaFactory(quantidade=5)
        bloqueio = BloqueioFactory(caravana=caravana)
        
        # Criar 2 passageiros vendidos
        for _ in range(2):
            PassageiroFactory(bloqueio=bloqueio)
        
        response = self.client.get(
            reverse('comercial:caravana_detalhes', kwargs={'caravana_id': caravana.id})
        )
        
        self.assertEqual(response.status_code, 200)
        # Range deve ser de 1 a 3 (3 vagas disponíveis)
        self.assertEqual(list(response.context['quantidade_range']), [1, 2, 3])
    
    def test_quantidade_range_sem_vagas(self):
        """Testa range quando não há vagas disponíveis"""
        caravana = CaravanaFactory(quantidade=2)
        bloqueio = BloqueioFactory(caravana=caravana)
        
        # Criar 2 passageiros (esgota vagas)
        for _ in range(2):
            PassageiroFactory(bloqueio=bloqueio)
        
        response = self.client.get(
            reverse('comercial:caravana_detalhes', kwargs={'caravana_id': caravana.id})
        )
        
        self.assertEqual(response.status_code, 200)
        # Range deve ser range(1, 1) = vazio
        self.assertEqual(list(response.context['quantidade_range']), [])
        self.assertEqual(response.context['passageiros_disponiveis'], 0)


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class ComercialAccessControlTest(TestCase):
    """Testes específicos para controle de acesso na área comercial"""
    
    def setUp(self):
        self.client = Client()
        
        # Criar grupos
        self.grupo_comercial = GroupFactory(name='Comercial')
        self.grupo_admin = GroupFactory(name='Administração')
        
        # Criar usuários com diferentes grupos
        self.user_comercial = UsuarioFactory()
        self.user_comercial.groups.add(self.grupo_comercial)
        
        self.user_admin = UsuarioFactory() 
        self.user_admin.groups.add(self.grupo_admin)
        
        self.user_sem_grupo = UsuarioFactory()
        
        # URLs da área comercial
        self.urls_comercial = [
            'comercial:home',
            'comercial:nova_venda', 
            'comercial:caravanas_disponiveis',
        ]
    
    def test_acesso_usuario_comercial(self):
        """Testa que usuário do grupo Comercial acessa todas as views"""
        self.client.force_login(self.user_comercial)
        
        for url_name in self.urls_comercial:
            with self.subTest(url=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)
    
    def test_acesso_negado_usuario_admin(self):
        """Testa que usuário apenas do grupo Administração é negado"""
        self.client.force_login(self.user_admin)
        
        for url_name in self.urls_comercial:
            with self.subTest(url=url_name):
                response = self.client.get(reverse(url_name))
                self.assertIn(response.status_code, [302, 403])
    
    def test_acesso_negado_usuario_sem_grupo(self):
        """Testa que usuário sem grupo é negado"""
        self.client.force_login(self.user_sem_grupo)
        
        for url_name in self.urls_comercial:
            with self.subTest(url=url_name):
                response = self.client.get(reverse(url_name))
                self.assertIn(response.status_code, [302, 403])
    
    def test_redirecionamento_usuario_nao_logado(self):
        """Testa redirecionamento para login quando usuário não está logado"""
        for url_name in self.urls_comercial:
            with self.subTest(url=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 302)
                self.assertIn('/login/', response.url)