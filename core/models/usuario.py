from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .pessoa import Pessoa
from core.managers import UsuarioManager


class Usuario(AbstractBaseUser, PermissionsMixin):
    pessoa = models.OneToOneField(
        Pessoa, on_delete=models.PROTECT, verbose_name="Pessoa"
    )
    username = models.CharField(
        max_length=150, unique=True, verbose_name="Nome de usuário"
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    is_staff = models.BooleanField(default=False, verbose_name="Equipe")
    date_joined = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de cadastro"
    )

    objects = UsuarioManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["pessoa"]

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return self.username

    @property
    def email(self):
        return self.pessoa.email

    @property
    def nome(self):
        return self.pessoa.nome
