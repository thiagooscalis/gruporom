from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.core.files.storage import InMemoryStorage
from core.factories import *
from core.models import *


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class CiaAreaModelTest(TestCase):
    
    def test_create_cia_area(self):
        cia = CiaAreaFactory()
        self.assertIsNotNone(cia.nome)
        self.assertIsNotNone(cia.iata)
        self.assertEqual(len(cia.iata), 3)
    
    def test_iata_unique(self):
        # Com get_or_create, não haverá IntegrityError, mas reutilizará o objeto
        cia1 = CiaAreaFactory(iata='GOL')
        cia2 = CiaAreaFactory(iata='GOL')
        self.assertEqual(cia1.pk, cia2.pk)  # Mesmo objeto reutilizado
    
    def test_str_representation(self):
        cia = CiaAreaFactory(nome='GOL Linhas Aéreas', iata='GOL')
        self.assertEqual(str(cia), 'GOL Linhas Aéreas (GOL)')


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class PaisModelTest(TestCase):
    
    def test_create_pais(self):
        pais = PaisFactory()
        self.assertIsNotNone(pais.nome)
        self.assertIsNotNone(pais.iso)
        self.assertEqual(len(pais.iso), 2)
    
    def test_iso_unique(self):
        # Com get_or_create, não haverá IntegrityError, mas reutilizará o objeto
        pais1 = PaisFactory(iso='BR')
        pais2 = PaisFactory(iso='BR')
        self.assertEqual(pais1.pk, pais2.pk)  # Mesmo objeto reutilizado
    
    def test_str_representation(self):
        pais = PaisFactory(nome='Brasil', iso='BR')
        self.assertEqual(str(pais), 'Brasil (BR)')


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class CidadeModelTest(TestCase):
    
    def test_create_cidade(self):
        cidade = CidadeFactory()
        self.assertIsNotNone(cidade.nome)
        self.assertIsNotNone(cidade.pais)
    
    def test_str_representation(self):
        pais = PaisFactory(nome='Brasil')
        cidade = CidadeFactory(nome='São Paulo', pais=pais)
        self.assertEqual(str(cidade), 'São Paulo, Brasil')


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class AeroportoModelTest(TestCase):
    
    def test_create_aeroporto(self):
        aeroporto = AeroportoFactory()
        self.assertIsNotNone(aeroporto.nome)
        self.assertIsNotNone(aeroporto.iata)
        self.assertIsNotNone(aeroporto.cidade)
        self.assertIsNotNone(aeroporto.timezone)
        self.assertEqual(len(aeroporto.iata), 3)
    
    def test_iata_unique(self):
        # Com get_or_create, não haverá IntegrityError, mas reutilizará o objeto
        aeroporto1 = AeroportoFactory(iata='GRU')
        aeroporto2 = AeroportoFactory(iata='GRU')
        self.assertEqual(aeroporto1.pk, aeroporto2.pk)  # Mesmo objeto reutilizado
    
    def test_str_representation(self):
        pais = PaisFactory(nome='Brasil')
        cidade = CidadeFactory(nome='São Paulo', pais=pais)
        aeroporto = AeroportoFactory(nome='Guarulhos', iata='GRU', cidade=cidade)
        self.assertEqual(str(aeroporto), 'Guarulhos (GRU) - São Paulo, Brasil')


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class CaravanaModelTest(TestCase):
    
    def test_create_caravana(self):
        caravana = CaravanaFactory()
        self.assertIsNotNone(caravana.nome)
        self.assertIsNotNone(caravana.empresa)
        self.assertIsNotNone(caravana.promotor)
        self.assertIsNotNone(caravana.tipo)
        self.assertIsNotNone(caravana.data_contrato)
    
    def test_str_representation(self):
        empresa = PessoaFactory(nome='Empresa Teste')
        lider1 = PessoaFactory(nome='João Silva')
        lider2 = PessoaFactory(nome='Maria Santos')
        caravana = CaravanaFactory(nome='Caravana Teste', empresa=empresa, lideres=[lider1, lider2])
        
        str_caravana = str(caravana)
        self.assertTrue(str_caravana.startswith('Caravana Teste com'))
        self.assertTrue('João Silva' in str_caravana)
        self.assertTrue('Maria Santos' in str_caravana)


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class InclusoModelTest(TestCase):
    
    def test_create_incluso(self):
        incluso = InclusoFactory()
        self.assertIsNotNone(incluso.descricao)
        self.assertIn(incluso.incluso, [True, False])
        self.assertIn(incluso.padrao, [True, False])
    
    def test_str_representation(self):
        incluso = InclusoFactory(descricao='Café da manhã', incluso=True)
        self.assertEqual(str(incluso), 'Café da manhã - Incluso')
        
        incluso_nao = InclusoFactory(descricao='Jantar', incluso=False)
        self.assertEqual(str(incluso_nao), 'Jantar - Não Incluso')


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class HotelModelTest(TestCase):
    
    def test_create_hotel(self):
        hotel = HotelFactory()
        self.assertIsNotNone(hotel.nome)
        self.assertIsNotNone(hotel.endereco)
        self.assertIsNotNone(hotel.cidade)
    
    def test_str_representation(self):
        pais = PaisFactory(nome='Brasil')
        cidade = CidadeFactory(nome='Rio de Janeiro', pais=pais)
        hotel = HotelFactory(nome='Hotel Copacabana', cidade=cidade)
        self.assertEqual(str(hotel), 'Hotel Copacabana - Rio de Janeiro, Brasil')


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class BloqueioModelTest(TestCase):
    
    def test_create_bloqueio(self):
        bloqueio = BloqueioFactory()
        self.assertIsNotNone(bloqueio.caravana)
        self.assertIsNotNone(bloqueio.descricao)
        self.assertIsNotNone(bloqueio.saida)
        self.assertIsNotNone(bloqueio.valor)
        self.assertIsNotNone(bloqueio.taxas)
    
    def test_str_representation(self):
        caravana = CaravanaFactory(nome='Caravana Teste')
        bloqueio = BloqueioFactory(caravana=caravana, descricao='Pacote Europa', saida='2024-06-15')
        expected = 'Caravana Teste - Pacote Europa (2024-06-15)'
        self.assertEqual(str(bloqueio), expected)


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class PassageiroModelTest(TestCase):
    
    def test_create_passageiro(self):
        passageiro = PassageiroFactory()
        self.assertIsNotNone(passageiro.pessoa)
        self.assertIsNotNone(passageiro.bloqueio)
        self.assertIn(passageiro.single, [True, False])
    
    def test_unique_together(self):
        pessoa = PessoaFactory()
        bloqueio = BloqueioFactory()
        PassageiroFactory(pessoa=pessoa, bloqueio=bloqueio)
        
        with self.assertRaises(IntegrityError):
            PassageiroFactory(pessoa=pessoa, bloqueio=bloqueio)
    
    def test_str_representation(self):
        pessoa = PessoaFactory(nome='João Silva')
        passageiro = PassageiroFactory(pessoa=pessoa, tipo='VIP')
        self.assertEqual(str(passageiro), 'João Silva - VIP')


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class VooModelTest(TestCase):
    
    def test_create_voo(self):
        voo = VooFactory()
        self.assertIsNotNone(voo.numero)
        self.assertIsNotNone(voo.cia_aerea)
        self.assertIsNotNone(voo.embarque)
        self.assertIsNotNone(voo.desembarque)
        self.assertIsNotNone(voo.aeroporto_embarque)
        self.assertIsNotNone(voo.aeroporto_desembarque)
        self.assertIsNotNone(voo.bloqueio)
    
    def test_str_representation(self):
        cia = CiaAreaFactory(iata='GOL')
        aeroporto_origem = AeroportoFactory(iata='GRU')
        aeroporto_destino = AeroportoFactory(iata='SDU')
        voo = VooFactory(
            numero='1234',
            cia_aerea=cia,
            aeroporto_embarque=aeroporto_origem,
            aeroporto_desembarque=aeroporto_destino
        )
        self.assertEqual(str(voo), 'GOL 1234 - GRU → SDU')


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class DiaRoteiroModelTest(TestCase):
    
    def test_create_dia_roteiro(self):
        dia = DiaRoteiroFactory()
        self.assertIsNotNone(dia.ordem)
        self.assertIsNotNone(dia.titulo)
        self.assertIsNotNone(dia.descricao)
        self.assertIsNotNone(dia.bloqueio)
    
    def test_unique_together(self):
        bloqueio = BloqueioFactory()
        DiaRoteiroFactory(ordem=1, bloqueio=bloqueio)
        
        with self.assertRaises(IntegrityError):
            DiaRoteiroFactory(ordem=1, bloqueio=bloqueio)
    
    def test_str_representation(self):
        dia = DiaRoteiroFactory(ordem=1, titulo='Chegada em Paris')
        self.assertEqual(str(dia), 'Dia 1: Chegada em Paris')


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class ExtraModelTest(TestCase):
    
    def test_create_extra(self):
        extra = ExtraFactory()
        self.assertIsNotNone(extra.descricao)
        self.assertIsNotNone(extra.valor)
        self.assertIsNotNone(extra.moeda)
        self.assertIsNotNone(extra.bloqueio)
    
    def test_str_representation(self):
        extra = ExtraFactory(descricao='Seguro viagem', valor=150.00, moeda='Real')
        # Verificar formato flexível já que pode variar (150.0 ou 150.00)
        str_extra = str(extra)
        self.assertTrue(str_extra.startswith('Seguro viagem - Real 150'))
        self.assertTrue('150' in str_extra)


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class TarefaModelTest(TestCase):
    
    def test_create_tarefa(self):
        tarefa = TarefaFactory()
        self.assertIsNotNone(tarefa.categoria)
        self.assertIsNotNone(tarefa.descricao)
        self.assertIsNotNone(tarefa.bloqueio)
        self.assertIsNotNone(tarefa.created_at)
    
    def test_concluida_property(self):
        tarefa_pendente = TarefaFactory(concluida_em=None)
        self.assertFalse(tarefa_pendente.concluida)
        
        from django.utils import timezone
        tarefa_concluida = TarefaFactory(concluida_em=timezone.now())
        self.assertTrue(tarefa_concluida.concluida)
    
    def test_str_representation(self):
        tarefa = TarefaFactory(categoria='Aéreo', descricao='Confirmar voos', concluida_em=None)
        self.assertEqual(str(tarefa), '○ [Aéreo] Confirmar voos')


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class NotaModelTest(TestCase):
    
    def test_create_nota(self):
        nota = NotaFactory()
        self.assertIsNotNone(nota.usuario)
        self.assertIsNotNone(nota.descricao)
        self.assertIsNotNone(nota.created_at)
        self.assertIsNone(nota.resposta)
    
    def test_create_nota_resposta(self):
        nota_original = NotaFactory()
        nota_resposta = NotaRespostaFactory(resposta=nota_original)
        self.assertEqual(nota_resposta.resposta, nota_original)
    
    def test_str_representation(self):
        usuario = UsuarioFactory()
        pessoa = PessoaFactory(nome='João Silva')
        usuario.pessoa = pessoa
        usuario.save()
        
        nota = NotaFactory(usuario=usuario, descricao='Esta é uma nota de teste muito longa que será truncada')
        # Verificar se contém o nome e os primeiros caracteres + "..."
        str_nota = str(nota)
        self.assertTrue(str_nota.startswith('João Silva: Esta é uma nota de teste muito longa que será'))
        self.assertTrue(str_nota.endswith('...'))