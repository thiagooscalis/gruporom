from django.test import TestCase, override_settings
from django.core.files.storage import InMemoryStorage
from core.factories import *


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class FactoriesTest(TestCase):
    """Testa se todas as factories conseguem criar objetos válidos"""
    
    def test_cia_area_factory(self):
        cia = CiaAreaFactory()
        self.assertIsNotNone(cia.pk)
        self.assertIsNotNone(cia.nome)
        self.assertEqual(len(cia.iata), 3)
    
    def test_pais_factory(self):
        pais = PaisFactory()
        self.assertIsNotNone(pais.pk)
        self.assertIsNotNone(pais.nome)
        self.assertEqual(len(pais.iso), 2)
    
    def test_cidade_factory(self):
        cidade = CidadeFactory()
        self.assertIsNotNone(cidade.pk)
        self.assertIsNotNone(cidade.nome)
        self.assertIsNotNone(cidade.pais)
    
    def test_aeroporto_factory(self):
        aeroporto = AeroportoFactory()
        self.assertIsNotNone(aeroporto.pk)
        self.assertIsNotNone(aeroporto.nome)
        self.assertEqual(len(aeroporto.iata), 3)
        self.assertIsNotNone(aeroporto.cidade)
        self.assertIsNotNone(aeroporto.timezone)
    
    def test_caravana_factory(self):
        caravana = CaravanaFactory()
        self.assertIsNotNone(caravana.pk)
        self.assertIsNotNone(caravana.nome)
        self.assertIsNotNone(caravana.empresa)
        self.assertIsNotNone(caravana.promotor)
        self.assertIsNotNone(caravana.tipo)
        self.assertGreater(caravana.lideres.count(), 0)
    
    def test_incluso_factory(self):
        incluso = InclusoFactory()
        self.assertIsNotNone(incluso.pk)
        self.assertIsNotNone(incluso.descricao)
        self.assertIn(incluso.incluso, [True, False])
        self.assertIn(incluso.padrao, [True, False])
    
    def test_hotel_factory(self):
        hotel = HotelFactory()
        self.assertIsNotNone(hotel.pk)
        self.assertIsNotNone(hotel.nome)
        self.assertIsNotNone(hotel.endereco)
        self.assertIsNotNone(hotel.cidade)
    
    def test_bloqueio_factory(self):
        bloqueio = BloqueioFactory()
        self.assertIsNotNone(bloqueio.pk)
        self.assertIsNotNone(bloqueio.caravana)
        self.assertIsNotNone(bloqueio.descricao)
        self.assertIsNotNone(bloqueio.saida)
        self.assertGreater(bloqueio.paises.count(), 0)
        self.assertGreater(bloqueio.inclusos.count(), 0)
        self.assertGreater(bloqueio.hoteis.count(), 0)
    
    def test_passageiro_factory(self):
        passageiro = PassageiroFactory()
        self.assertIsNotNone(passageiro.pk)
        self.assertIsNotNone(passageiro.pessoa)
        self.assertIsNotNone(passageiro.bloqueio)
        self.assertIn(passageiro.single, [True, False])
    
    def test_voo_factory(self):
        voo = VooFactory()
        self.assertIsNotNone(voo.pk)
        self.assertIsNotNone(voo.numero)
        self.assertIsNotNone(voo.cia_aerea)
        self.assertIsNotNone(voo.embarque)
        self.assertIsNotNone(voo.desembarque)
        self.assertIsNotNone(voo.aeroporto_embarque)
        self.assertIsNotNone(voo.aeroporto_desembarque)
        self.assertIsNotNone(voo.bloqueio)
        # Desembarque deve ser após embarque
        self.assertGreater(voo.desembarque, voo.embarque)
    
    def test_dia_roteiro_factory(self):
        dia = DiaRoteiroFactory()
        self.assertIsNotNone(dia.pk)
        self.assertIsNotNone(dia.ordem)
        self.assertIsNotNone(dia.titulo)
        self.assertIsNotNone(dia.descricao)
        self.assertIsNotNone(dia.bloqueio)
    
    def test_extra_factory(self):
        extra = ExtraFactory()
        self.assertIsNotNone(extra.pk)
        self.assertIsNotNone(extra.descricao)
        self.assertIsNotNone(extra.valor)
        self.assertIsNotNone(extra.moeda)
        self.assertIsNotNone(extra.bloqueio)
    
    def test_tarefa_factory(self):
        tarefa = TarefaFactory()
        self.assertIsNotNone(tarefa.pk)
        self.assertIsNotNone(tarefa.categoria)
        self.assertIsNotNone(tarefa.descricao)
        self.assertIsNotNone(tarefa.bloqueio)
        self.assertIsNotNone(tarefa.created_at)
    
    def test_nota_factory(self):
        nota = NotaFactory()
        self.assertIsNotNone(nota.pk)
        self.assertIsNotNone(nota.usuario)
        self.assertIsNotNone(nota.descricao)
        self.assertIsNotNone(nota.created_at)
        self.assertIsNone(nota.resposta)
    
    def test_nota_resposta_factory(self):
        nota_resposta = NotaRespostaFactory()
        self.assertIsNotNone(nota_resposta.pk)
        self.assertIsNotNone(nota_resposta.usuario)
        self.assertIsNotNone(nota_resposta.descricao)
        self.assertIsNotNone(nota_resposta.resposta)
    
    def test_batch_creation(self):
        """Testa criação em lote para verificar performance"""
        caravanas = CaravanaFactory.create_batch(5)
        self.assertEqual(len(caravanas), 5)
        
        bloqueios = BloqueioFactory.create_batch(3)
        self.assertEqual(len(bloqueios), 3)
        
        passageiros = PassageiroFactory.create_batch(10)
        self.assertEqual(len(passageiros), 10)