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
    empresas = models.ManyToManyField(
        Pessoa,
        limit_choices_to={'empresa_gruporom': True},
        blank=True,
        verbose_name="Empresas do Grupo ROM",
        related_name="usuarios_empresa"
    )
    gerente_comercial = models.BooleanField(
        default=False,
        verbose_name="Gerente Comercial",
        help_text="Usuário possui permissões gerenciais na área comercial"
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
        return self.pessoa.email_principal

    @property
    def nome(self):
        return self.pessoa.nome

    def save(self, *args, **kwargs):
        """Sobrescreve save para gerenciar permissões automaticamente"""
        is_update = self.pk is not None
        old_gerente_comercial = None
        
        if is_update:
            old_instance = Usuario.objects.get(pk=self.pk)
            old_gerente_comercial = old_instance.gerente_comercial
        
        super().save(*args, **kwargs)
        
        # Gerencia permissões apenas se o campo mudou
        if not is_update or old_gerente_comercial != self.gerente_comercial:
            self._update_controle_whatsapp_permission()
    
    def _update_controle_whatsapp_permission(self):
        """Atualiza a permissão controle_whatsapp baseada no status de gerente comercial"""
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        # Cria a permissão se não existir
        content_type = ContentType.objects.get_for_model(self.__class__)
        permission, created = Permission.objects.get_or_create(
            codename='controle_whatsapp',
            defaults={
                'name': 'Pode gerenciar WhatsApp Business',
                'content_type': content_type,
            }
        )
        
        if self.gerente_comercial:
            # Adiciona a permissão
            self.user_permissions.add(permission)
        else:
            # Remove a permissão
            self.user_permissions.remove(permission)
        
        # Limpa o cache de permissões para refletir as mudanças imediatamente
        if hasattr(self, '_user_perm_cache'):
            delattr(self, '_user_perm_cache')
        if hasattr(self, '_group_perm_cache'):
            delattr(self, '_group_perm_cache')
        if hasattr(self, '_perm_cache'):
            delattr(self, '_perm_cache')
