from django.db import models
from django.core.validators import RegexValidator


class Telefone(models.Model):
    """
    Model para telefones vinculados a pessoas
    """
    
    pessoa = models.ForeignKey(
        'Pessoa',
        on_delete=models.CASCADE,
        related_name='telefones',
        verbose_name='Pessoa'
    )
    
    # DDI - Código do país (ex: 55 para Brasil)
    ddi = models.CharField(
        max_length=4,
        validators=[
            RegexValidator(
                regex=r'^\d{1,4}$',
                message='DDI deve conter apenas números (1-4 dígitos)'
            )
        ],
        verbose_name='DDI',
        help_text='Código do país (ex: 55 para Brasil)'
    )
    
    # DDD - Código de área (ex: 11 para São Paulo)
    ddd = models.CharField(
        max_length=3,
        validators=[
            RegexValidator(
                regex=r'^\d{2,3}$',
                message='DDD deve conter 2-3 números'
            )
        ],
        verbose_name='DDD',
        help_text='Código de área (ex: 11)'
    )
    
    # Número do telefone
    telefone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\d{7,15}$',
                message='Telefone deve conter apenas números (7-15 dígitos)'
            )
        ],
        verbose_name='Telefone'
    )
    
    # Tipo de telefone
    TIPO_CHOICES = [
        ('celular', 'Celular'),
        ('residencial', 'Residencial'),
        ('comercial', 'Comercial'),
        ('whatsapp', 'WhatsApp'),
        ('outro', 'Outro'),
    ]
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='celular',
        verbose_name='Tipo'
    )
    
    # Telefone principal (apenas um por pessoa pode ser principal)
    principal = models.BooleanField(
        default=False,
        verbose_name='Principal'
    )
    
    # Campos de controle
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Telefone'
        verbose_name_plural = 'Telefones'
        ordering = ['-principal', '-criado_em']
        indexes = [
            models.Index(fields=['pessoa', 'principal']),
            models.Index(fields=['ddi', 'ddd', 'telefone']),
        ]
    
    def __str__(self):
        return f"+{self.ddi} ({self.ddd}) {self.telefone}"
    
    @property
    def numero_completo(self):
        """Retorna número no formato internacional completo"""
        return f"+{self.ddi}{self.ddd}{self.telefone}"
    
    @property
    def numero_formatado(self):
        """Retorna número formatado para exibição"""
        if len(self.telefone) == 9:  # Celular
            return f"+{self.ddi} ({self.ddd}) {self.telefone[:5]}-{self.telefone[5:]}"
        elif len(self.telefone) == 8:  # Fixo
            return f"+{self.ddi} ({self.ddd}) {self.telefone[:4]}-{self.telefone[4:]}"
        else:
            return f"+{self.ddi} ({self.ddd}) {self.telefone}"
    
    def save(self, *args, **kwargs):
        # Se marcado como principal, remove principal dos outros telefones da pessoa
        if self.principal:
            Telefone.objects.filter(pessoa=self.pessoa, principal=True).update(principal=False)
        
        super().save(*args, **kwargs)


class Email(models.Model):
    """
    Model para emails vinculados a pessoas
    """
    
    pessoa = models.ForeignKey(
        'Pessoa',
        on_delete=models.CASCADE,
        related_name='emails',
        verbose_name='Pessoa'
    )
    
    email = models.EmailField(
        verbose_name='E-mail'
    )
    
    # Tipo de email
    TIPO_CHOICES = [
        ('pessoal', 'Pessoal'),
        ('profissional', 'Profissional'),
        ('comercial', 'Comercial'),
        ('outro', 'Outro'),
    ]
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='pessoal',
        verbose_name='Tipo'
    )
    
    # Email principal (apenas um por pessoa pode ser principal)
    principal = models.BooleanField(
        default=False,
        verbose_name='Principal'
    )
    
    # Campos de controle
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    verificado = models.BooleanField(default=False, verbose_name='Verificado')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'E-mail'
        verbose_name_plural = 'E-mails'
        ordering = ['-principal', '-criado_em']
        unique_together = [['pessoa', 'email']]  # Evita email duplicado para mesma pessoa
        indexes = [
            models.Index(fields=['pessoa', 'principal']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.get_tipo_display()})"
    
    def save(self, *args, **kwargs):
        # Se marcado como principal, remove principal dos outros emails da pessoa
        if self.principal:
            Email.objects.filter(pessoa=self.pessoa, principal=True).update(principal=False)
        
        super().save(*args, **kwargs)