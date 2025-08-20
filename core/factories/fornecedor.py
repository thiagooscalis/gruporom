import factory
from factory.django import DjangoModelFactory
from core.models import Fornecedor
from core.choices import TIPO_EMPRESA_CHOICES


class FornecedorFactory(DjangoModelFactory):
    class Meta:
        model = Fornecedor
        skip_postgeneration_save = True
    
    pessoa = factory.SubFactory('core.factories.PessoaJuridicaFactory')
    tipo_empresa = factory.Faker('random_element', elements=[choice[0] for choice in TIPO_EMPRESA_CHOICES])
    
    @factory.post_generation
    def empresas(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            for empresa in extracted:
                self.empresas.add(empresa)
        else:
            # Adiciona 1-2 empresas do grupo ROM
            from core.factories import PessoaFactory
            import random
            empresas = PessoaFactory.create_batch(
                random.randint(1, 2),
                empresa_gruporom=True,
                tipo_doc='CNPJ'
            )
            for empresa in empresas:
                self.empresas.add(empresa)