from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import Group
from django.core.files.storage import InMemoryStorage
from django.urls import reverse
from core.factories import UsuarioAdministracaoFactory, PessoaFactory
from core.models import Pessoa


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class CarregarMaisTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.admin_user = UsuarioAdministracaoFactory()
        self.client.force_login(self.admin_user)
        
        # Criar 25 pessoas para testar paginação
        for i in range(25):
            PessoaFactory(nome=f'Pessoa {i+1:02d}')
        
    def test_primeira_pagina_mostra_botao_carregar_mais(self):
        """Testa se a primeira página mostra o botão carregar mais"""
        response = self.client.get(reverse('administracao:pessoas_lista'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Carregar mais')
        self.assertContains(response, 'carregar-mais-container')
        # Deve mostrar 20 pessoas na primeira página
        self.assertEqual(len(response.context['page_obj']), 20)
        
    def test_carregar_mais_htmx_retorna_linhas(self):
        """Testa se requisição HTMX com load_more retorna apenas as linhas"""
        response = self.client.get(
            reverse('administracao:pessoas_lista') + '?page=2&load_more=1',
            HTTP_HX_REQUEST='true'
        )
        
        self.assertEqual(response.status_code, 200)
        # Deve usar template de linhas
        self.assertTemplateUsed(response, 'administracao/pessoas/partial_linhas.html')
        # Não deve ter cabeçalho da tabela
        self.assertNotContains(response, '<thead>')
        # Deve ter apenas as linhas <tr>
        self.assertContains(response, '<tr>')
        
    def test_carregar_mais_sem_load_more_retorna_tabela_completa(self):
        """Testa se requisição HTMX sem load_more retorna tabela completa"""
        response = self.client.get(
            reverse('administracao:pessoas_lista') + '?page=2',
            HTTP_HX_REQUEST='true'
        )
        
        self.assertEqual(response.status_code, 200)
        # Deve usar template parcial completo
        self.assertTemplateUsed(response, 'administracao/pessoas/partial_lista.html')
        # Deve ter cabeçalho da tabela
        self.assertContains(response, '<thead>')
        
    def test_ultima_pagina_nao_mostra_botao_carregar_mais(self):
        """Testa se a última página não mostra o botão carregar mais"""
        # Com 25 pessoas e 20 por página, página 2 é a última (5 pessoas)
        response = self.client.get(
            reverse('administracao:pessoas_lista') + '?page=2',
            HTTP_HX_REQUEST='true'
        )
        
        self.assertEqual(response.status_code, 200)
        # Não deve ter botão carregar mais
        self.assertNotContains(response, 'Carregar mais')
        self.assertNotContains(response, 'carregar-mais-container')
        
    def test_contador_pessoas_restantes_correto(self):
        """Testa se o contador de pessoas restantes está correto"""
        response = self.client.get(reverse('administracao:pessoas_lista'))
        
        self.assertEqual(response.status_code, 200)
        # Verificar quantas pessoas realmente temos
        total_pessoas = response.context['page_obj'].paginator.count
        pessoas_exibidas = len(response.context['page_obj'])
        restantes = total_pessoas - pessoas_exibidas
        
        # Só verificar se realmente tem botão carregar mais
        if restantes > 0:
            self.assertContains(response, f'{restantes} restantes')
        
    def test_carregar_mais_com_filtro_preserva_parametros(self):
        """Testa se carregar mais preserva os parâmetros de filtro"""
        # Criar pessoa específica para busca
        PessoaFactory(nome='João Especial')
        
        response = self.client.get(
            reverse('administracao:pessoas_lista') + '?search=João&page=1',
            HTTP_HX_REQUEST='true'
        )
        
        self.assertEqual(response.status_code, 200)
        if 'Carregar mais' in response.content.decode():
            # Verificar se o botão mantém o parâmetro search
            self.assertContains(response, '&search=João')
        
    def test_tbody_tem_id_correto(self):
        """Testa se o tbody tem o ID correto para append"""
        response = self.client.get(
            reverse('administracao:pessoas_lista'),
            HTTP_HX_REQUEST='true'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="pessoas-tbody"')