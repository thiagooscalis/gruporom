# -*- coding: utf-8 -*-
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Group
from core.models import Fornecedor
from core.choices import TIPO_EMPRESA_CHOICES
from core.factories import PessoaFactory, EmpresaGrupoROMFactory, UsuarioFactory


@pytest.mark.django_db
class FornecedorCadastroTestCase(TestCase):
    """Testes para cadastro de fornecedores via HTMX"""

    def setUp(self):
        """Setup para cada teste"""
        self.client = Client()
        
        # Criar grupo Administração
        self.admin_group = Group.objects.create(name='Administração')
        
        # Criar usuário admin
        self.admin_user = UsuarioFactory()
        self.admin_user.groups.add(self.admin_group)
        
        # Criar pessoa para ser fornecedor
        self.pessoa_fornecedor = PessoaFactory(
            nome="João Silva Fornecedor",
            tipo_doc="CPF",
            doc="12345678901",
            email1="joao@fornecedor.com"
        )
        
        # Criar empresas do Grupo ROM
        self.empresa1 = EmpresaGrupoROMFactory(
            nome="US Travel Operadora",
            doc="12345678000195"
        )
        self.empresa2 = EmpresaGrupoROMFactory(
            nome="ROM Turismo Ltda",
            doc="98765432000187"
        )
        
        # URLs
        self.list_url = reverse('administracao:fornecedores_lista')
        self.create_url = reverse('administracao:fornecedores_criar')
        self.modal_url = reverse('administracao:fornecedores_novo_modal')

    def test_acesso_nao_autorizado(self):
        """Testa que usuário não logado não acessa as páginas"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 302)  # Redirect para login
        
        response = self.client.post(self.create_url)
        self.assertEqual(response.status_code, 302)  # Redirect para login

    def test_listagem_fornecedores_vazia(self):
        """Testa listagem quando não há fornecedores"""
        self.client.force_login(self.admin_user)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, 200)
        # Verificar mensagem de nenhum fornecedor cadastrado
        self.assertContains(response, "Nenhum fornecedor cadastrado")

    def test_modal_novo_fornecedor(self):
        """Testa abertura do modal de novo fornecedor"""
        self.client.force_login(self.admin_user)
        response = self.client.get(self.modal_url, HTTP_HX_REQUEST='true')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Novo Fornecedor")
        self.assertContains(response, "form")
        self.assertContains(response, "pessoa")
        self.assertContains(response, "tipo_empresa")
        self.assertContains(response, "empresas")

    def test_cadastro_fornecedor_sucesso(self):
        """Testa cadastro de fornecedor com sucesso"""
        self.client.force_login(self.admin_user)
        
        data = {
            'pessoa': self.pessoa_fornecedor.pk,
            'tipo_empresa': 'Turismo',
            'empresas': [self.empresa1.pk, self.empresa2.pk]
        }
        
        response = self.client.post(
            self.create_url, 
            data,
            HTTP_HX_REQUEST='true'
        )
        
        # Deve retornar script de sucesso
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<script>')
        self.assertContains(response, 'htmx.ajax')
        
        # Verificar se fornecedor foi criado
        self.assertTrue(Fornecedor.objects.exists())
        fornecedor = Fornecedor.objects.first()
        self.assertEqual(fornecedor.pessoa, self.pessoa_fornecedor)
        self.assertEqual(fornecedor.tipo_empresa, 'Turismo')
        self.assertEqual(fornecedor.empresas.count(), 2)
        self.assertIn(self.empresa1, fornecedor.empresas.all())
        self.assertIn(self.empresa2, fornecedor.empresas.all())

    def test_cadastro_fornecedor_sem_pessoa(self):
        """Testa erro quando não seleciona pessoa"""
        self.client.force_login(self.admin_user)
        
        data = {
            'pessoa': '',
            'tipo_empresa': 'Turismo',
            'empresas': [self.empresa1.pk]
        }
        
        response = self.client.post(
            self.create_url,
            data,
            HTTP_HX_REQUEST='true'
        )
        
        # Deve retornar formulário com erro
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        # Verificar se há erro de validação (campo obrigatório)
        self.assertContains(response, 'Este campo é obrigatório', msg_prefix="Deve conter mensagem de campo obrigatório")
        
        # Não deve criar fornecedor
        self.assertFalse(Fornecedor.objects.exists())

    def test_cadastro_fornecedor_sem_tipo_empresa(self):
        """Testa erro quando não seleciona tipo de empresa"""
        self.client.force_login(self.admin_user)
        
        data = {
            'pessoa': self.pessoa_fornecedor.pk,
            'tipo_empresa': '',
            'empresas': [self.empresa1.pk]
        }
        
        response = self.client.post(
            self.create_url,
            data,
            HTTP_HX_REQUEST='true'
        )
        
        # Deve retornar formulário com erro
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # Não deve criar fornecedor
        self.assertFalse(Fornecedor.objects.exists())

    def test_cadastro_fornecedor_sem_empresas(self):
        """Testa erro quando não seleciona nenhuma empresa"""
        self.client.force_login(self.admin_user)
        
        data = {
            'pessoa': self.pessoa_fornecedor.pk,
            'tipo_empresa': 'Turismo',
            'empresas': []
        }
        
        response = self.client.post(
            self.create_url,
            data,
            HTTP_HX_REQUEST='true'
        )
        
        # Deve retornar formulário com erro (empresas é obrigatório)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # Não deve criar fornecedor
        self.assertFalse(Fornecedor.objects.exists())

    def test_cadastro_fornecedor_pessoa_ja_e_fornecedor(self):
        """Testa erro quando pessoa já é fornecedor"""
        self.client.force_login(self.admin_user)
        
        # Criar fornecedor existente
        fornecedor_existente = Fornecedor.objects.create(
            pessoa=self.pessoa_fornecedor,
            tipo_empresa='Alimentação'
        )
        fornecedor_existente.empresas.add(self.empresa1)
        
        data = {
            'pessoa': self.pessoa_fornecedor.pk,
            'tipo_empresa': 'Turismo',
            'empresas': [self.empresa2.pk]
        }
        
        response = self.client.post(
            self.create_url,
            data,
            HTTP_HX_REQUEST='true'
        )
        
        # Deve retornar formulário com erro
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertContains(response, 'já é um fornecedor')
        
        # Deve ter apenas 1 fornecedor (o original)
        self.assertEqual(Fornecedor.objects.count(), 1)

    def test_todas_opcoes_tipo_empresa_disponiveis(self):
        """Testa se todas as opções de tipo de empresa estão disponíveis"""
        self.client.force_login(self.admin_user)
        response = self.client.get(self.modal_url, HTTP_HX_REQUEST='true')
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se todas as opções estão presentes
        for codigo, descricao in TIPO_EMPRESA_CHOICES:
            if codigo:  # Não verificar opção vazia
                self.assertContains(response, descricao)

    def test_apenas_empresas_grupo_rom_disponiveis(self):
        """Testa se apenas empresas do Grupo ROM estão disponíveis"""
        self.client.force_login(self.admin_user)
        
        # Criar pessoa que NÃO é empresa do Grupo ROM
        pessoa_comum = PessoaFactory(
            nome="Pessoa Comum",
            empresa_gruporom=False
        )
        
        response = self.client.get(self.modal_url, HTTP_HX_REQUEST='true')
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que empresas do Grupo ROM estão presentes
        self.assertContains(response, self.empresa1.nome)
        self.assertContains(response, self.empresa2.nome)
        
        # Verificar que pessoa comum NÃO está presente
        self.assertNotContains(response, pessoa_comum.nome)

    def test_listagem_apos_cadastro(self):
        """Testa se fornecedor aparece na listagem após cadastro"""
        self.client.force_login(self.admin_user)
        
        # Criar fornecedor
        fornecedor = Fornecedor.objects.create(
            pessoa=self.pessoa_fornecedor,
            tipo_empresa='Turismo'
        )
        fornecedor.empresas.add(self.empresa1)
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.pessoa_fornecedor.nome)
        self.assertContains(response, 'Turismo')
        self.assertNotContains(response, "Nenhum fornecedor cadastrado")

    def test_busca_fornecedor(self):
        """Testa busca de fornecedores"""
        self.client.force_login(self.admin_user)
        
        # Criar fornecedores
        fornecedor1 = Fornecedor.objects.create(
            pessoa=self.pessoa_fornecedor,
            tipo_empresa='Turismo'
        )
        fornecedor1.empresas.add(self.empresa1)
        
        pessoa2 = PessoaFactory(nome="Maria Santos", doc="98765432100")
        fornecedor2 = Fornecedor.objects.create(
            pessoa=pessoa2,
            tipo_empresa='Alimentação'
        )
        fornecedor2.empresas.add(self.empresa2)
        
        # Buscar por nome
        response = self.client.get(self.list_url + '?search=João')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "João Silva")
        self.assertNotContains(response, "Maria Santos")
        
        # Buscar por tipo de empresa
        response = self.client.get(self.list_url + '?search=Alimentação')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maria Santos")
        self.assertNotContains(response, "João Silva")

    def test_cadastro_fornecedor_com_uma_empresa(self):
        """Testa cadastro de fornecedor selecionando apenas uma empresa"""
        self.client.force_login(self.admin_user)
        
        data = {
            'pessoa': self.pessoa_fornecedor.pk,
            'tipo_empresa': 'Administração de Bens',
            'empresas': [self.empresa1.pk]  # Apenas uma empresa
        }
        
        response = self.client.post(
            self.create_url,
            data,
            HTTP_HX_REQUEST='true'
        )
        
        # Deve ter sucesso
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<script>')
        
        # Verificar fornecedor criado
        self.assertTrue(Fornecedor.objects.exists())
        fornecedor = Fornecedor.objects.first()
        self.assertEqual(fornecedor.empresas.count(), 1)
        self.assertIn(self.empresa1, fornecedor.empresas.all())

    def test_htmx_headers_requeridos(self):
        """Testa se views respondem corretamente a requisições HTMX"""
        self.client.force_login(self.admin_user)
        
        # Requisição normal (sem HTMX)
        response = self.client.get(self.modal_url)
        self.assertEqual(response.status_code, 200)
        
        # Requisição HTMX
        response = self.client.get(self.modal_url, HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        
        # Ambas devem funcionar, mas conteúdo pode ser diferente
        self.assertContains(response, 'form')