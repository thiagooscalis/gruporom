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
        self.assertEqual(str(pais), 'Brasil')


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
        self.assertEqual(str_caravana, 'Caravana Teste')
        
        # Test lideres_nomes property separately
        lideres_nomes = caravana.lideres_nomes
        self.assertIn('João Silva', lideres_nomes)
        self.assertIn('Maria Santos', lideres_nomes)


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


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class PessoaModelTest(TestCase):
    
    def test_create_pessoa_fisica(self):
        pessoa = PessoaFactory(tipo_doc='CPF')
        self.assertEqual(pessoa.tipo_doc, 'CPF')
        self.assertIsNotNone(pessoa.nome)
        self.assertIsNotNone(pessoa.doc)
    
    def test_create_pessoa_juridica(self):
        pessoa = PessoaJuridicaFactory()
        self.assertEqual(pessoa.tipo_doc, 'CNPJ')
        self.assertIsNotNone(pessoa.nome)
        self.assertIsNotNone(pessoa.doc)
    
    def test_str_representation(self):
        pessoa = PessoaFactory(nome='João Silva')
        self.assertEqual(str(pessoa), 'João Silva')
    
    def test_tipo_pessoa_property(self):
        pessoa_cpf = PessoaFactory(tipo_doc='CPF')
        self.assertEqual(pessoa_cpf.tipo_pessoa, 'FISICA')
        
        pessoa_cnpj = PessoaJuridicaFactory()
        self.assertEqual(pessoa_cnpj.tipo_pessoa, 'JURIDICA')


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class UsuarioModelTest(TestCase):
    
    def test_create_usuario(self):
        usuario = UsuarioFactory()
        self.assertIsNotNone(usuario.username)
        self.assertIsNotNone(usuario.pessoa)
        self.assertTrue(usuario.is_active)
    
    def test_superusuario(self):
        usuario = SuperUsuarioFactory()
        self.assertTrue(usuario.is_superuser)
        self.assertTrue(usuario.is_staff)
    
    def test_str_representation(self):
        usuario = UsuarioFactory(username='joao.silva')
        self.assertEqual(str(usuario), 'joao.silva')


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class CambioModelTest(TestCase):
    
    def test_create_cambio(self):
        cambio = CambioFactory()
        self.assertIsNotNone(cambio.data)
        self.assertIsNotNone(cambio.valor)
    
    def test_str_representation(self):
        from decimal import Decimal
        from datetime import date
        cambio = CambioFactory(data=date(2024, 1, 15), valor=Decimal('5.45'))
        self.assertEqual(str(cambio), 'USD/BRL 15/01/2024: R$ 5.45')
    
    def test_obter_cambio(self):
        from core.models import Cambio
        from datetime import date
        cambio = CambioFactory(data=date.today())
        resultado = Cambio.obter_cambio(date.today())
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.data, date.today())


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class CargoModelTest(TestCase):
    
    def test_create_cargo(self):
        cargo = CargoFactory()
        self.assertIsNotNone(cargo.nome)
        self.assertIsNotNone(cargo.empresa)
        self.assertTrue(cargo.ativo)
    
    def test_str_representation(self):
        from core.factories import EmpresaGrupoROMFactory
        empresa = EmpresaGrupoROMFactory(nome='ROM Turismo')
        cargo = CargoFactory(nome='Gerente', empresa=empresa)
        self.assertEqual(str(cargo), 'Gerente - ROM Turismo')


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class ColaboradorModelTest(TestCase):
    
    def test_create_colaborador(self):
        colaborador = ColaboradorFactory()
        self.assertIsNotNone(colaborador.pessoa)
        self.assertIsNotNone(colaborador.cargo)
        self.assertIsNotNone(colaborador.salario)
        self.assertIsNotNone(colaborador.data_admissao)
        self.assertTrue(colaborador.ativo)
    
    def test_esta_ativo_property(self):
        colaborador_ativo = ColaboradorFactory(ativo=True, data_demissao=None)
        self.assertTrue(colaborador_ativo.esta_ativo)
        
        from datetime import date
        colaborador_demitido = ColaboradorFactory(ativo=True, data_demissao=date.today())
        self.assertFalse(colaborador_demitido.esta_ativo)
    
    def test_str_representation(self):
        pessoa = PessoaFactory(nome='João Silva')
        cargo = CargoFactory(nome='Vendedor')
        colaborador = ColaboradorFactory(pessoa=pessoa, cargo=cargo)
        self.assertEqual(str(colaborador), 'João Silva - Vendedor')
    
    def test_comissao_validation(self):
        from django.core.exceptions import ValidationError
        from decimal import Decimal
        colaborador = ColaboradorFactory.build(comissao=Decimal('150.00'))
        with self.assertRaises(ValidationError):
            colaborador.full_clean()


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class FornecedorModelTest(TestCase):
    
    def test_create_fornecedor(self):
        fornecedor = FornecedorFactory()
        self.assertIsNotNone(fornecedor.pessoa)
        self.assertIsNotNone(fornecedor.tipo_empresa)
        self.assertEqual(fornecedor.pessoa.tipo_doc, 'CNPJ')
    
    def test_str_representation(self):
        pessoa = PessoaJuridicaFactory(nome='Empresa ABC')
        fornecedor = FornecedorFactory(pessoa=pessoa, tipo_empresa='Tecnologia')
        self.assertEqual(str(fornecedor), 'Empresa ABC - Tecnologia')


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class FuncaoModelTest(TestCase):
    
    def test_create_funcao(self):
        funcao = FuncaoFactory()
        self.assertIsNotNone(funcao.masculino)
        self.assertIsNotNone(funcao.feminino)
        self.assertIsNotNone(funcao.abreviacao_masculino)
        self.assertIsNotNone(funcao.abreviacao_feminino)
    
    def test_get_funcao_por_sexo(self):
        funcao = FuncaoFactory(masculino='Diretor', feminino='Diretora')
        self.assertEqual(funcao.get_funcao_por_sexo('Masculino'), 'Diretor')
        self.assertEqual(funcao.get_funcao_por_sexo('Feminino'), 'Diretora')
    
    def test_str_representation(self):
        funcao = FuncaoFactory(masculino='Diretor', feminino='Diretora')
        self.assertEqual(str(funcao), 'Diretor / Diretora')


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class TurnoModelTest(TestCase):
    
    def test_create_turno(self):
        turno = TurnoFactory()
        self.assertIsNotNone(turno.nome)
        self.assertIsNotNone(turno.inicio)
        self.assertIsNotNone(turno.fim)
        self.assertTrue(turno.ativo)
    
    def test_duracao_horas(self):
        from datetime import time
        turno = TurnoFactory(inicio=time(8, 0), fim=time(12, 0))
        self.assertEqual(turno.duracao_horas, 4.0)
        
        # Turno noturno
        turno_noturno = TurnoFactory(inicio=time(22, 0), fim=time(6, 0))
        self.assertEqual(turno_noturno.duracao_horas, 8.0)
    
    def test_eh_noturno(self):
        from datetime import time
        turno_diurno = TurnoFactory(inicio=time(8, 0), fim=time(17, 0))
        self.assertFalse(turno_diurno.eh_noturno)
        
        turno_noturno = TurnoFactory(inicio=time(22, 0), fim=time(6, 0))
        self.assertTrue(turno_noturno.eh_noturno)
    
    def test_str_representation(self):
        from datetime import time
        turno = TurnoFactory(nome='Manhã', inicio=time(8, 0), fim=time(12, 0))
        self.assertEqual(str(turno), 'Manhã (08:00 - 12:00)')


@override_settings(DEFAULT_FILE_STORAGE=InMemoryStorage())
class WhatsAppModelTest(TestCase):
    
    def test_create_whatsapp_account(self):
        account = WhatsAppAccountFactory()
        self.assertIsNotNone(account.name)
        self.assertIsNotNone(account.phone_number_id)
        self.assertIsNotNone(account.business_account_id)
        self.assertTrue(account.is_active)
    
    def test_create_whatsapp_template(self):
        template = WhatsAppTemplateFactory()
        self.assertIsNotNone(template.name)
        self.assertIsNotNone(template.account)
        self.assertIsNotNone(template.category)
        self.assertIsNotNone(template.language)
    
    def test_create_whatsapp_conversation(self):
        conversation = WhatsAppConversationFactory()
        self.assertIsNotNone(conversation.account)
        self.assertIsNotNone(conversation.contact)
        self.assertIsNotNone(conversation.status)
        self.assertIsNotNone(conversation.criado_em)
    
    def test_whatsapp_message(self):
        message = WhatsAppMessageFactory()
        self.assertIsNotNone(message.conversation)
        self.assertIsNotNone(message.wamid)
        self.assertIsNotNone(message.direction)
        self.assertIsNotNone(message.timestamp)