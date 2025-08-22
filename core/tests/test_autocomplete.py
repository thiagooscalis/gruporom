# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.contrib.auth.models import Group
from django.urls import reverse
from core.factories import UsuarioAdministracaoFactory, PessoaFactory, UsuarioFactory


class BuscarPessoasViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.admin_user = UsuarioAdministracaoFactory()
        self.client.force_login(self.admin_user)
        
        # Criar pessoas de teste
        self.pessoa1 = PessoaFactory(
            nome='João Silva Santos',
            doc='12345678901',
            email1='joao@email.com'
        )
        self.pessoa2 = PessoaFactory(
            nome='Maria Oliveira',
            doc='98765432100',
            email1='maria@email.com'
        )
        self.pessoa3 = PessoaFactory(
            nome='Pedro Costa',
            doc='11122233344',
            email1='pedro@email.com'
        )
        
        # Criar pessoa com usuário vinculado
        self.usuario_com_pessoa = UsuarioFactory()
        self.pessoa_com_usuario = self.usuario_com_pessoa.pessoa
        
    def test_buscar_pessoas_sem_query_minima(self):
        """Testa busca com menos de 2 caracteres"""
        response = self.client.get(
            reverse('buscar_pessoas', kwargs={'area': 'administracao'}),
            {'q': 'J'}
        )
        
        self.assertEqual(response.status_code, 200)
        # A view retorna com o query, então mostra mensagem de "não encontrado"
        self.assertContains(response, 'Nenhuma pessoa encontrada para "J"')
        # Não deve retornar pessoas
        context_pessoas = response.context.get('pessoas', [])
        self.assertEqual(len(context_pessoas), 0)
        
    def test_buscar_pessoas_por_nome(self):
        """Testa busca por nome"""
        response = self.client.get(
            reverse('buscar_pessoas', kwargs={'area': 'administracao'}),
            {'q': 'João'}
        )
        
        self.assertEqual(response.status_code, 200)
        context_pessoas = list(response.context['pessoas'])
        self.assertIn(self.pessoa1, context_pessoas)
        self.assertNotIn(self.pessoa2, context_pessoas)
        
    def test_buscar_pessoas_por_documento(self):
        """Testa busca por documento"""
        response = self.client.get(
            reverse('buscar_pessoas', kwargs={'area': 'administracao'}),
            {'q': '123456'}
        )
        
        self.assertEqual(response.status_code, 200)
        context_pessoas = list(response.context['pessoas'])
        self.assertIn(self.pessoa1, context_pessoas)
        self.assertNotIn(self.pessoa2, context_pessoas)
        
    def test_buscar_pessoas_por_email(self):
        """Testa busca por email"""
        response = self.client.get(
            reverse('buscar_pessoas', kwargs={'area': 'administracao'}),
            {'q': 'joao@'}
        )
        
        self.assertEqual(response.status_code, 200)
        context_pessoas = list(response.context['pessoas'])
        self.assertIn(self.pessoa1, context_pessoas)
        self.assertNotIn(self.pessoa2, context_pessoas)
        
    def test_buscar_pessoas_sem_usuario_padrao(self):
        """Testa que por padrão só retorna pessoas sem usuário"""
        response = self.client.get(
            reverse('buscar_pessoas', kwargs={'area': 'administracao'}),
            {'q': self.pessoa_com_usuario.nome[:4]}
        )
        
        self.assertEqual(response.status_code, 200)
        context_pessoas = list(response.context['pessoas'])
        self.assertNotIn(self.pessoa_com_usuario, context_pessoas)
        
    def test_buscar_pessoas_com_all_true(self):
        """Testa busca com all=true incluindo pessoas com usuário"""
        response = self.client.get(
            reverse('buscar_pessoas', kwargs={'area': 'administracao'}),
            {'q': self.pessoa_com_usuario.nome[:4], 'all': 'true'}
        )
        
        self.assertEqual(response.status_code, 200)
        context_pessoas = list(response.context['pessoas'])
        self.assertIn(self.pessoa_com_usuario, context_pessoas)
        
    def test_buscar_pessoas_limite_20_resultados(self):
        """Testa limite de 20 resultados"""
        # Criar 25 pessoas com nome similar
        for i in range(25):
            PessoaFactory(nome=f'Teste {i}')
        
        response = self.client.get(
            reverse('buscar_pessoas', kwargs={'area': 'administracao'}),
            {'q': 'Teste'}
        )
        
        self.assertEqual(response.status_code, 200)
        context_pessoas = list(response.context['pessoas'])
        self.assertEqual(len(context_pessoas), 20)
        
    def test_buscar_pessoas_field_id_no_contexto(self):
        """Testa se field_id é passado para o contexto"""
        response = self.client.get(
            reverse('buscar_pessoas', kwargs={'area': 'administracao'}),
            {'q': 'João', 'field_id': 'id_responsavel'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['field_id'], 'id_responsavel')
        
    def test_buscar_pessoas_sem_autenticacao(self):
        """Testa acesso sem autenticação"""
        self.client.logout()
        response = self.client.get(
            reverse('buscar_pessoas', kwargs={'area': 'administracao'}),
            {'q': 'João'}
        )
        
        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        
    def test_buscar_pessoas_sem_grupo_correto(self):
        """Testa acesso sem grupo da área"""
        # Criar usuário sem grupo administração
        usuario_sem_grupo = UsuarioFactory()
        self.client.force_login(usuario_sem_grupo)
        
        response = self.client.get(
            reverse('buscar_pessoas', kwargs={'area': 'administracao'}),
            {'q': 'João'}
        )
        
        # Deve retornar 403 Forbidden
        self.assertEqual(response.status_code, 403)


class BuscarPessoasParaEdicaoViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.admin_user = UsuarioAdministracaoFactory()
        self.client.force_login(self.admin_user)
        
        # Criar pessoas de teste
        self.pessoa1 = PessoaFactory(nome='João Silva')
        self.pessoa2 = PessoaFactory(nome='Maria Oliveira')
        
        # Criar usuário com pessoa vinculada
        self.usuario_edicao = UsuarioFactory()
        self.pessoa_do_usuario = self.usuario_edicao.pessoa
        
        # Criar pessoa com outro usuário
        self.outro_usuario = UsuarioFactory()
        self.pessoa_outro_usuario = self.outro_usuario.pessoa
        
    def test_buscar_pessoas_edicao_sem_query_minima(self):
        """Testa busca para edição com menos de 2 caracteres"""
        response = self.client.get(
            reverse('buscar_pessoas_edicao', kwargs={'area': 'administracao'}),
            {'q': 'J'}
        )
        
        self.assertEqual(response.status_code, 200)
        context_pessoas = response.context.get('pessoas', [])
        self.assertEqual(len(context_pessoas), 0)
        
    def test_buscar_pessoas_edicao_inclui_pessoa_atual(self):
        """Testa que busca inclui a pessoa do usuário sendo editado"""
        response = self.client.get(
            reverse('buscar_pessoas_edicao', kwargs={'area': 'administracao'}),
            {
                'q': self.pessoa_do_usuario.nome[:4],
                'usuario_id': self.usuario_edicao.pk
            }
        )
        
        self.assertEqual(response.status_code, 200)
        context_pessoas = list(response.context['pessoas'])
        self.assertIn(self.pessoa_do_usuario, context_pessoas)
        
    def test_buscar_pessoas_edicao_exclui_outras_com_usuario(self):
        """Testa que busca exclui pessoas com outros usuários"""
        response = self.client.get(
            reverse('buscar_pessoas_edicao', kwargs={'area': 'administracao'}),
            {
                'q': self.pessoa_outro_usuario.nome[:4],
                'usuario_id': self.usuario_edicao.pk
            }
        )
        
        self.assertEqual(response.status_code, 200)
        context_pessoas = list(response.context['pessoas'])
        self.assertNotIn(self.pessoa_outro_usuario, context_pessoas)
        
    def test_buscar_pessoas_edicao_inclui_pessoas_sem_usuario(self):
        """Testa que busca inclui pessoas sem usuário"""
        response = self.client.get(
            reverse('buscar_pessoas_edicao', kwargs={'area': 'administracao'}),
            {
                'q': self.pessoa1.nome[:4],
                'usuario_id': self.usuario_edicao.pk
            }
        )
        
        self.assertEqual(response.status_code, 200)
        context_pessoas = list(response.context['pessoas'])
        self.assertIn(self.pessoa1, context_pessoas)
        
    def test_buscar_pessoas_edicao_sem_usuario_id(self):
        """Testa busca sem usuario_id especificado"""
        response = self.client.get(
            reverse('buscar_pessoas_edicao', kwargs={'area': 'administracao'}),
            {'q': self.pessoa1.nome[:4]}
        )
        
        self.assertEqual(response.status_code, 200)
        context_pessoas = list(response.context['pessoas'])
        self.assertIn(self.pessoa1, context_pessoas)
        # Não deve incluir pessoas com usuário
        self.assertNotIn(self.pessoa_do_usuario, context_pessoas)
        
    def test_buscar_pessoas_edicao_field_id_contexto(self):
        """Testa se field_id é passado para o contexto"""
        response = self.client.get(
            reverse('buscar_pessoas_edicao', kwargs={'area': 'administracao'}),
            {
                'q': 'João',
                'field_id': 'id_pessoa',
                'usuario_id': self.usuario_edicao.pk
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['field_id'], 'id_pessoa')


class AutocompleteIntegrationTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.admin_user = UsuarioAdministracaoFactory()
        self.client.force_login(self.admin_user)
        
    def test_autocomplete_template_response(self):
        """Testa se o template correto é renderizado"""
        response = self.client.get(
            reverse('buscar_pessoas', kwargs={'area': 'administracao'}),
            {'q': 'test'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'components/pessoas_autocomplete.html')
        
    def test_autocomplete_headers_ajax(self):
        """Testa resposta com headers AJAX"""
        response = self.client.get(
            reverse('buscar_pessoas', kwargs={'area': 'administracao'}),
            {'q': 'test'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        
    def test_autocomplete_diferentes_areas(self):
        """Testa autocomplete em diferentes áreas"""
        
        # Criar grupos necessários
        grupos = ['Comercial', 'Operacional']
        for grupo_nome in grupos:
            Group.objects.get_or_create(name=grupo_nome)
        
        # Testar administração (usuário já tem acesso)
        response = self.client.get(
            reverse('buscar_pessoas', kwargs={'area': 'administracao'}),
            {'q': 'test'}
        )
        self.assertEqual(response.status_code, 200)
        
        # Testar outras áreas adicionando grupos ao usuário
        for grupo_nome, area in [('Comercial', 'comercial'), ('Operacional', 'operacional')]:
            grupo = Group.objects.get(name=grupo_nome)
            self.admin_user.groups.add(grupo)
            
            response = self.client.get(
                reverse('buscar_pessoas', kwargs={'area': area}),
                {'q': 'test'}
            )
            self.assertEqual(response.status_code, 200)
            
    def test_autocomplete_ordenacao_por_nome(self):
        """Testa se resultados são ordenados por nome"""
        PessoaFactory(nome='Zebra')
        PessoaFactory(nome='Alberto')
        PessoaFactory(nome='Carlos')
        
        response = self.client.get(
            reverse('buscar_pessoas', kwargs={'area': 'administracao'}),
            {'q': 'a'}  # Busca que pega Alberto, Carlos, Zebra
        )
        
        self.assertEqual(response.status_code, 200)
        pessoas = list(response.context['pessoas'])
        
        # Verifica se está ordenado
        nomes = [p.nome for p in pessoas]
        self.assertEqual(nomes, sorted(nomes))