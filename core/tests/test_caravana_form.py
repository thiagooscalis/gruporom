# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import Group
from decimal import Decimal
from datetime import date, timedelta
from core.forms.caravana import CaravanaForm
from core.models import Caravana, Bloqueio
from core.factories import UsuarioFactory, PessoaFactory


class CaravanaFormTest(TestCase):
    """
    Testes para o formulário de Caravana com criação automática de bloqueios
    """
    
    def setUp(self):
        """Configuração inicial dos testes"""
        # Criar grupos necessários
        self.operacional_group = Group.objects.get_or_create(name='Operacional')[0]
        
        # Criar usuário de teste
        self.user = UsuarioFactory()
        self.user.groups.add(self.operacional_group)
        
        # Criar pessoas para teste
        self.empresa = PessoaFactory(
            tipo_doc='CNPJ',
            empresa_gruporom=True,
            nome='Empresa Teste'
        )
        
        # Criar pessoas com usuários ativos para promotor e líderes
        self.promotor = PessoaFactory(nome='Promotor Teste')
        self.promotor_user = UsuarioFactory(pessoa=self.promotor, is_active=True)
        
        self.lider1 = PessoaFactory(nome='Líder 1')
        self.lider1_user = UsuarioFactory(pessoa=self.lider1, is_active=True)
        
        self.lider2 = PessoaFactory(nome='Líder 2')
        self.lider2_user = UsuarioFactory(pessoa=self.lider2, is_active=True)
        
    def test_form_fields_presence(self):
        """Testa se todos os campos necessários estão presentes no formulário"""
        form = CaravanaForm(user=self.user)
        
        # Campos da caravana
        self.assertIn('nome', form.fields)
        self.assertIn('empresa', form.fields)
        self.assertIn('tipo', form.fields)
        self.assertIn('promotor', form.fields)
        self.assertIn('lideres', form.fields)
        self.assertIn('quantidade', form.fields)
        
        # Campos dos bloqueios
        self.assertIn('data_saida', form.fields)
        self.assertIn('valor_economica', form.fields)
        self.assertIn('valor_executiva', form.fields)
        self.assertIn('valor_terrestre', form.fields)
        self.assertIn('taxas', form.fields)
        self.assertIn('moeda_valor', form.fields)
        self.assertIn('moeda_taxas', form.fields)
        
    def test_form_initial_values(self):
        """Testa se os valores iniciais estão corretos"""
        form = CaravanaForm(user=self.user)
        
        self.assertEqual(form.fields['taxas'].initial, 0)
        self.assertEqual(form.fields['moeda_valor'].initial, 'Dólar')
        self.assertEqual(form.fields['moeda_taxas'].initial, 'Dólar')
        
    def test_valid_form_creation(self):
        """Testa criação de caravana válida com dados corretos"""
        data = {
            'nome': 'Caravana Teste',
            'empresa': self.empresa.pk,
            'tipo': 'Evangélica',
            'promotor': self.promotor.pk,
            'lideres': [self.lider1.pk, self.lider2.pk],
            'quantidade': 50,
            'free_economica': 2,
            'free_executiva': 1,
            'repasse_valor': Decimal('1000.00'),
            'repasse_tipo': 'Total',
            'data_contrato': date.today(),
            'destaque_site': 0,
            
            # Dados dos bloqueios
            'data_saida': date.today() + timedelta(days=30),
            'valor_economica': Decimal('2500.00'),
            'valor_executiva': Decimal('3500.00'),
            'valor_terrestre': Decimal('1200.00'),
            'taxas': Decimal('150.00'),
            'moeda_valor': 'Dólar',
            'moeda_taxas': 'Dólar',
        }
        
        form = CaravanaForm(data=data, user=self.user)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
    def test_form_validation_free_exceeds_quantity(self):
        """Testa validação quando free excede quantidade total"""
        data = {
            'nome': 'Caravana Teste',
            'empresa': self.empresa.pk,
            'tipo': 'Evangélica',
            'promotor': self.promotor.pk,
            'quantidade': 10,
            'free_economica': 8,
            'free_executiva': 5,  # 8 + 5 = 13 > 10
            'repasse_valor': Decimal('1000.00'),
            'repasse_tipo': 'Total',
            'data_contrato': date.today(),
            'destaque_site': 0,
            
            # Dados dos bloqueios
            'data_saida': date.today() + timedelta(days=30),
            'valor_economica': Decimal('2500.00'),
            'valor_executiva': Decimal('3500.00'),
            'valor_terrestre': Decimal('1200.00'),
            'taxas': Decimal('150.00'),
            'moeda_valor': 'Dólar',
            'moeda_taxas': 'Dólar',
        }
        
        form = CaravanaForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('quantidade', form.errors)
        
    def test_save_creates_three_bloqueios(self):
        """Testa se ao salvar a caravana são criados os 3 bloqueios automaticamente"""
        data = {
            'nome': 'Caravana com Bloqueios',
            'empresa': self.empresa.pk,
            'tipo': 'Evangélica',
            'promotor': self.promotor.pk,
            'lideres': [self.lider1.pk],
            'quantidade': 40,
            'free_economica': 1,
            'free_executiva': 1,
            'repasse_valor': Decimal('800.00'),
            'repasse_tipo': 'Total',
            'data_contrato': date.today(),
            'destaque_site': 0,
            
            # Dados dos bloqueios
            'data_saida': date.today() + timedelta(days=45),
            'valor_economica': Decimal('2000.00'),
            'valor_executiva': Decimal('3000.00'),
            'valor_terrestre': Decimal('1000.00'),
            'taxas': Decimal('100.00'),
            'moeda_valor': 'Dólar',
            'moeda_taxas': 'Real',
        }
        
        form = CaravanaForm(data=data, user=self.user)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        # Verificar que não existem bloqueios antes
        self.assertEqual(Bloqueio.objects.count(), 0)
        
        # Salvar a caravana
        caravana = form.save()
        
        # Verificar que a caravana foi criada
        self.assertIsInstance(caravana, Caravana)
        self.assertEqual(caravana.nome, 'Caravana com Bloqueios')
        
        # Verificar que 3 bloqueios foram criados
        bloqueios = Bloqueio.objects.filter(caravana=caravana)
        self.assertEqual(bloqueios.count(), 3)
        
        # Verificar os nomes dos bloqueios
        descricoes = bloqueios.values_list('descricao', flat=True)
        self.assertIn('Econômica', descricoes)
        self.assertIn('Executiva', descricoes)
        self.assertIn('Terrestre', descricoes)
        
        # Verificar dados específicos dos bloqueios
        bloqueio_economica = bloqueios.get(descricao='Econômica')
        self.assertEqual(bloqueio_economica.valor, Decimal('2000.00'))
        self.assertEqual(bloqueio_economica.taxas, Decimal('100.00'))
        self.assertEqual(bloqueio_economica.moeda_valor, 'Dólar')
        self.assertEqual(bloqueio_economica.moeda_taxas, 'Real')
        self.assertFalse(bloqueio_economica.terrestre)
        self.assertTrue(bloqueio_economica.ativo)
        
        bloqueio_executiva = bloqueios.get(descricao='Executiva')
        self.assertEqual(bloqueio_executiva.valor, Decimal('3000.00'))
        self.assertFalse(bloqueio_executiva.terrestre)
        
        bloqueio_terrestre = bloqueios.get(descricao='Terrestre')
        self.assertEqual(bloqueio_terrestre.valor, Decimal('1000.00'))
        self.assertTrue(bloqueio_terrestre.terrestre)
        
    def test_edit_existing_caravana_doesnt_create_bloqueios(self):
        """Testa que ao editar uma caravana existente não cria novos bloqueios"""
        # Criar uma caravana primeiro
        data = {
            'nome': 'Caravana Original',
            'empresa': self.empresa.pk,
            'tipo': 'Evangélica',
            'promotor': self.promotor.pk,
            'lideres': [self.lider1.pk],
            'quantidade': 30,
            'free_economica': 1,
            'free_executiva': 0,
            'repasse_valor': Decimal('500.00'),
            'repasse_tipo': 'Total',
            'data_contrato': date.today(),
            'destaque_site': 0,
            
            # Dados dos bloqueios
            'data_saida': date.today() + timedelta(days=60),
            'valor_economica': Decimal('1800.00'),
            'valor_executiva': Decimal('2800.00'),
            'valor_terrestre': Decimal('900.00'),
            'taxas': Decimal('80.00'),
            'moeda_valor': 'Dólar',
            'moeda_taxas': 'Dólar',
        }
        
        form = CaravanaForm(data=data, user=self.user)
        caravana = form.save()
        
        # Verificar que 3 bloqueios foram criados
        self.assertEqual(Bloqueio.objects.filter(caravana=caravana).count(), 3)
        
        # Editar a caravana
        edit_data = data.copy()
        edit_data['nome'] = 'Caravana Editada'
        edit_data['quantidade'] = 35
        
        edit_form = CaravanaForm(data=edit_data, instance=caravana, user=self.user)
        self.assertTrue(edit_form.is_valid())
        
        caravana_editada = edit_form.save()
        
        # Verificar que ainda tem apenas 3 bloqueios (não criou novos)
        self.assertEqual(Bloqueio.objects.filter(caravana=caravana_editada).count(), 3)
        
        # Verificar que o nome foi atualizado
        caravana_editada.refresh_from_db()
        self.assertEqual(caravana_editada.nome, 'Caravana Editada')
        self.assertEqual(caravana_editada.quantidade, 35)

    def test_form_filtering_pessoas_ativas(self):
        """Testa se o formulário filtra apenas pessoas com usuários ativos"""
        # Criar pessoa com usuário inativo
        pessoa_inativa = PessoaFactory(nome='Pessoa Inativa')
        usuario_inativo = UsuarioFactory(pessoa=pessoa_inativa, is_active=False)
        
        form = CaravanaForm(user=self.user)
        
        # Verificar que pessoas com usuários ativos estão disponíveis
        promotor_ids = form.fields['promotor'].queryset.values_list('id', flat=True)
        lideres_ids = form.fields['lideres'].queryset.values_list('id', flat=True)
        
        self.assertIn(self.promotor.id, promotor_ids)
        self.assertIn(self.lider1.id, lideres_ids)
        
        # Verificar que pessoa com usuário inativo NÃO está disponível
        self.assertNotIn(pessoa_inativa.id, promotor_ids)
        self.assertNotIn(pessoa_inativa.id, lideres_ids)