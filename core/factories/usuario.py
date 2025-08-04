import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import Group
from core.models import Usuario
from core.factories.pessoa import PessoaFactory


class UsuarioFactory(DjangoModelFactory):
    class Meta:
        model = Usuario

    username = factory.Sequence(lambda n: f"usuario{n}")
    pessoa = factory.SubFactory(PessoaFactory)
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Define a senha do usuário"""
        if not create:
            return
        
        if extracted:
            obj.set_password(extracted)
        else:
            obj.set_password("senha123")

    @factory.post_generation
    def groups(obj, create, extracted, **kwargs):
        """Adiciona grupos ao usuário"""
        if not create:
            return
            
        if extracted:
            for group in extracted:
                obj.groups.add(group)


class SuperUsuarioFactory(UsuarioFactory):
    """Factory para criar superusuários"""
    
    username = factory.Sequence(lambda n: f"admin{n}")
    is_staff = True
    is_superuser = True


class UsuarioAdministracaoFactory(UsuarioFactory):
    """Factory para usuário do grupo Administração"""
    
    @factory.post_generation
    def groups(obj, create, extracted, **kwargs):
        if not create:
            return
            
        grupo, _ = Group.objects.get_or_create(name="Administração")
        obj.groups.add(grupo)


class GroupFactory(DjangoModelFactory):
    """Factory para criar grupos"""
    
    class Meta:
        model = Group
        django_get_or_create = ("name",)
    
    name = factory.Sequence(lambda n: f"Grupo {n}")