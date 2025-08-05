# -*- coding: utf-8 -*-
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from .pessoa import Pessoa
from .usuario import Usuario


class WhatsAppAccount(models.Model):
    """
    Model para contas do WhatsApp Business conectadas
    """
    
    ACCOUNT_STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('active', 'Ativo'),
        ('suspended', 'Suspenso'),
        ('disabled', 'Desabilitado'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name="Nome da Conta",
        help_text="Nome identificador da conta WhatsApp Business"
    )
    
    phone_number_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Phone Number ID",
        help_text="ID do número de telefone na API do WhatsApp"
    )
    
    phone_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+[1-9]\d{1,14}$',
                message='Número deve estar no formato internacional (+5511999999999)'
            )
        ],
        verbose_name="Número de Telefone",
        help_text="Número no formato internacional"
    )
    
    app_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="ID do Aplicativo",
        help_text="App ID obtido no Facebook for Developers"
    )
    
    app_secret = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Chave Secreta do Aplicativo", 
        help_text="App Secret obtido no Facebook for Developers"
    )
    
    access_token = models.TextField(
        verbose_name="Token de Acesso",
        help_text="Token de acesso permanente para a API"
    )
    
    webhook_verify_token = models.CharField(
        max_length=255,
        verbose_name="Token de Verificação Webhook",
        help_text="Token para verificação do webhook"
    )
    
    business_account_id = models.CharField(
        max_length=50,
        verbose_name="Business Account ID",
        help_text="ID da conta de negócios do WhatsApp"
    )
    
    status = models.CharField(
        max_length=20,
        choices=ACCOUNT_STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    # Relacionamento com usuário responsável
    responsavel = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="whatsapp_accounts",
        verbose_name="Responsável"
    )
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Conta WhatsApp"
        verbose_name_plural = "Contas WhatsApp"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.phone_number})"
    
    @property
    def display_phone(self):
        """Formata o número para exibição"""
        if self.phone_number.startswith('+55'):
            # Formato brasileiro
            number = self.phone_number[3:]
            if len(number) == 11:
                return f"({number[:2]}) {number[2:7]}-{number[7:]}"
            elif len(number) == 10:
                return f"({number[:2]}) {number[2:6]}-{number[6:]}"
        return self.phone_number


class WhatsAppContact(models.Model):
    """
    Model para contatos do WhatsApp
    """
    
    account = models.ForeignKey(
        WhatsAppAccount,
        on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name="Conta WhatsApp"
    )
    
    phone_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+[1-9]\d{1,14}$',
                message='Número deve estar no formato internacional (+5511999999999)'
            )
        ],
        verbose_name="Número de Telefone"
    )
    
    name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nome",
        help_text="Nome do contato no WhatsApp"
    )
    
    # Relacionamento opcional com pessoa do sistema
    pessoa = models.ForeignKey(
        Pessoa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="whatsapp_contacts",
        verbose_name="Pessoa Relacionada"
    )
    
    # Metadados do contato
    profile_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nome do Perfil"
    )
    
    is_business = models.BooleanField(
        default=False,
        verbose_name="É Empresa"
    )
    
    last_seen = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última Visualização"
    )
    
    is_blocked = models.BooleanField(
        default=False,
        verbose_name="Bloqueado"
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Contato WhatsApp"
        verbose_name_plural = "Contatos WhatsApp"
        unique_together = ['account', 'phone_number']
        ordering = ['name', 'phone_number']
    
    def __str__(self):
        return f"{self.name or self.phone_number} ({self.account.name})"
    
    @property
    def display_name(self):
        """Retorna o melhor nome disponível"""
        return self.name or self.profile_name or self.phone_number
    
    @property
    def display_phone(self):
        """Formata o número para exibição"""
        if self.phone_number.startswith('+55'):
            # Formato brasileiro
            number = self.phone_number[3:]
            if len(number) == 11:
                return f"({number[:2]}) {number[2:7]}-{number[7:]}"
            elif len(number) == 10:
                return f"({number[:2]}) {number[2:6]}-{number[6:]}"
        return self.phone_number


class WhatsAppMessage(models.Model):
    """
    Model para mensagens do WhatsApp
    """
    
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Texto'),
        ('image', 'Imagem'),
        ('document', 'Documento'),
        ('audio', 'Áudio'),
        ('video', 'Vídeo'),
        ('sticker', 'Figurinha'),
        ('location', 'Localização'),
        ('contacts', 'Contatos'),
        ('template', 'Template'),
        ('interactive', 'Interativo'),
        ('system', 'Sistema'),
    ]
    
    MESSAGE_STATUS_CHOICES = [
        ('sent', 'Enviada'),
        ('delivered', 'Entregue'),
        ('read', 'Lida'),
        ('failed', 'Falhou'),
        ('pending', 'Pendente'),
    ]
    
    DIRECTION_CHOICES = [
        ('inbound', 'Recebida'),
        ('outbound', 'Enviada'),
    ]
    
    # Identificadores
    wamid = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="WhatsApp Message ID",
        help_text="ID único da mensagem no WhatsApp"
    )
    
    account = models.ForeignKey(
        WhatsAppAccount,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Conta WhatsApp"
    )
    
    contact = models.ForeignKey(
        WhatsAppContact,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Contato"
    )
    
    # Direção e tipo da mensagem
    direction = models.CharField(
        max_length=10,
        choices=DIRECTION_CHOICES,
        verbose_name="Direção"
    )
    
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        verbose_name="Tipo"
    )
    
    # Conteúdo da mensagem
    content = models.TextField(
        blank=True,
        verbose_name="Conteúdo",
        help_text="Texto da mensagem ou dados JSON para outros tipos"
    )
    
    # Metadados de mídia (quando aplicável)
    media_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ID da Mídia"
    )
    
    media_url = models.URLField(
        blank=True,
        verbose_name="URL da Mídia"
    )
    
    media_filename = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nome do Arquivo"
    )
    
    media_mimetype = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tipo MIME"
    )
    
    # Status e timestamps
    status = models.CharField(
        max_length=20,
        choices=MESSAGE_STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    
    timestamp = models.DateTimeField(
        verbose_name="Timestamp da Mensagem",
        help_text="Timestamp original do WhatsApp"
    )
    
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Entregue em"
    )
    
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Lida em"
    )
    
    # Mensagem de resposta (threading)
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name="Resposta para"
    )
    
    # Contexto adicional
    context_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Dados de Contexto",
        help_text="Dados adicionais da mensagem (buttons, lists, etc.)"
    )
    
    # Usuário que enviou (para mensagens outbound)
    sent_by = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="whatsapp_messages_sent",
        verbose_name="Enviada por"
    )
    
    # Metadados do sistema
    error_message = models.TextField(
        blank=True,
        verbose_name="Mensagem de Erro"
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Mensagem WhatsApp"
        verbose_name_plural = "Mensagens WhatsApp"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['account', 'contact', '-timestamp']),
            models.Index(fields=['direction', '-timestamp']),
            models.Index(fields=['status', '-timestamp']),
        ]
    
    def __str__(self):
        direction_icon = "→" if self.direction == 'outbound' else "←"
        return f"{direction_icon} {self.contact.display_name}: {self.get_display_content()[:50]}"
    
    def get_display_content(self):
        """Retorna conteúdo formatado para exibição"""
        if self.message_type == 'text':
            return self.content
        elif self.message_type == 'image':
            return f"📷 Imagem: {self.media_filename or 'sem nome'}"
        elif self.message_type == 'document':
            return f"📄 Documento: {self.media_filename or 'sem nome'}"
        elif self.message_type == 'audio':
            return f"🎵 Áudio: {self.media_filename or 'mensagem de voz'}"
        elif self.message_type == 'video':
            return f"🎥 Vídeo: {self.media_filename or 'sem nome'}"
        elif self.message_type == 'sticker':
            return "🎭 Figurinha"
        elif self.message_type == 'location':
            return "📍 Localização"
        elif self.message_type == 'contacts':
            return "👤 Contatos"
        else:
            return f"[{self.get_message_type_display()}]"
    
    @property
    def is_media(self):
        """Verifica se a mensagem contém mídia"""
        return self.message_type in ['image', 'document', 'audio', 'video', 'sticker']
    
    @property
    def age(self):
        """Retorna a idade da mensagem"""
        return timezone.now() - self.timestamp
    
    def mark_as_read(self):
        """Marca a mensagem como lida"""
        if self.status != 'read':
            self.status = 'read'
            self.read_at = timezone.now()
            self.save(update_fields=['status', 'read_at', 'atualizado_em'])
    
    def mark_as_delivered(self):
        """Marca a mensagem como entregue"""
        if self.status == 'sent':
            self.status = 'delivered'
            self.delivered_at = timezone.now()
            self.save(update_fields=['status', 'delivered_at', 'atualizado_em'])


class WhatsAppTemplate(models.Model):
    """
    Model para templates de mensagens do WhatsApp Business
    """
    
    TEMPLATE_CATEGORY_CHOICES = [
        ('marketing', 'Marketing'),
        ('utility', 'Utilidade'),
        ('authentication', 'Autenticação'),
    ]
    
    TEMPLATE_STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('disabled', 'Desabilitado'),
    ]
    
    LANGUAGE_CHOICES = [
        ('pt_BR', 'Português (Brasil)'),
        ('en_US', 'Inglês (EUA)'),
        ('es_ES', 'Espanhol'),
        ('en', 'Inglês'),
        ('pt', 'Português'),
    ]
    
    account = models.ForeignKey(
        WhatsAppAccount,
        on_delete=models.CASCADE,
        related_name='templates',
        verbose_name="Conta WhatsApp"
    )
    
    name = models.CharField(
        max_length=512,
        verbose_name="Nome do Template",
        help_text="Nome único do template (apenas letras minúsculas, números e _)"
    )
    
    display_name = models.CharField(
        max_length=255,
        verbose_name="Nome de Exibição",
        help_text="Nome amigável para exibição na interface"
    )
    
    category = models.CharField(
        max_length=20,
        choices=TEMPLATE_CATEGORY_CHOICES,
        verbose_name="Categoria"
    )
    
    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='pt_BR',
        verbose_name="Idioma"
    )
    
    header_text = models.TextField(
        blank=True,
        max_length=60,
        verbose_name="Cabeçalho",
        help_text="Texto do cabeçalho (máximo 60 caracteres)"
    )
    
    body_text = models.TextField(
        max_length=1024,
        verbose_name="Corpo da Mensagem",
        help_text="Texto principal do template. Use {{1}}, {{2}} para variáveis"
    )
    
    footer_text = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Rodapé",
        help_text="Texto do rodapé (máximo 60 caracteres)"
    )
    
    # Campos para controle da API do WhatsApp
    template_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ID do Template",
        help_text="ID retornado pela API do WhatsApp"
    )
    
    status = models.CharField(
        max_length=20,
        choices=TEMPLATE_STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    
    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Motivo da Rejeição",
        help_text="Motivo da rejeição retornado pela API"
    )
    
    # Controle de botões (opcional)
    has_buttons = models.BooleanField(
        default=False,
        verbose_name="Tem Botões"
    )
    
    buttons_config = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Configuração dos Botões",
        help_text="JSON com configuração dos botões"
    )
    
    # Exemplos de variáveis para aprovação
    variables_examples = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Exemplos de Variáveis",
        help_text="Exemplos das variáveis {{1}}, {{2}}, etc. para envio à API"
    )
    
    # Campos de auditoria
    criado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='whatsapp_templates_criados',
        verbose_name="Criado por"
    )
    
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    class Meta:
        db_table = 'whatsapp_template'
        verbose_name = 'Template WhatsApp'
        verbose_name_plural = 'Templates WhatsApp'
        unique_together = ['account', 'name', 'language']
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"{self.display_name} ({self.get_language_display()})"
    
    @property
    def variables_count(self):
        """Conta quantas variáveis {{n}} existem no template"""
        import re
        text = f"{self.header_text} {self.body_text} {self.footer_text}"
        matches = re.findall(r'\{\{(\d+)\}\}', text)
        return len(set(matches)) if matches else 0
    
    @property
    def preview_text(self):
        """Retorna uma prévia do template"""
        preview = []
        if self.header_text:
            preview.append(f"**{self.header_text}**")
        preview.append(self.body_text)
        if self.footer_text:
            preview.append(f"_{self.footer_text}_")
        return "\n\n".join(preview)
    
    def get_status_badge_class(self):
        """Retorna classe CSS para badge do status"""
        status_classes = {
            'pending': 'bg-warning',
            'approved': 'bg-success',
            'rejected': 'bg-danger',
            'disabled': 'bg-secondary',
        }
        return status_classes.get(self.status, 'bg-secondary')
    
    def can_be_used(self):
        """Verifica se o template pode ser usado para envio"""
        return self.status == 'approved' and self.is_active
