from django.db import models
from django.utils.text import slugify
from core.choices import TIPO_DOC_CHOICES, SEXO_CHOICES, TIPO_EMPRESA_CHOICES


class Pessoa(models.Model):

    nome = models.CharField(max_length=255, verbose_name="Nome")
    slug = models.SlugField(max_length=255, editable=False)
    doc = models.CharField(
        max_length=20, unique=True, verbose_name="Documento"
    )
    tipo_doc = models.CharField(
        max_length=20,
        choices=TIPO_DOC_CHOICES,
        verbose_name="Tipo de Documento",
    )
    endereco = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Endereço"
    )
    numero = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Número"
    )
    complemento = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Complemento"
    )
    bairro = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Bairro"
    )
    cidade = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Cidade"
    )
    estado = models.CharField(
        max_length=2, blank=True, null=True, verbose_name="Estado"
    )
    pais = models.ForeignKey(
        'Pais',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="País"
    )
    cep = models.CharField(
        max_length=10, blank=True, null=True, verbose_name="CEP"
    )
    foto = models.ImageField(
        upload_to="pessoas/fotos/", blank=True, null=True, verbose_name="Foto"
    )
    passaporte_numero = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Número do Passaporte",
    )
    passaporte_validade = models.DateField(
        blank=True, null=True, verbose_name="Validade do Passaporte"
    )
    passaporte_copia = models.FileField(
        upload_to="pessoas/passaportes/",
        blank=True,
        null=True,
        verbose_name="Cópia do Passaporte",
    )
    passaporte_nome = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nome no Passaporte",
    )
    nascimento = models.DateField(
        blank=True, null=True, verbose_name="Data de Nascimento"
    )
    sexo = models.CharField(
        max_length=10,
        choices=SEXO_CHOICES,
        blank=True,
        null=True,
        verbose_name="Sexo",
    )
    funcao = models.ForeignKey(
        'Funcao',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Função"
    )
    empresa_gruporom = models.BooleanField(
        default=False,
        verbose_name="Empresa do Grupo ROM"
    )
    tipo_empresa = models.CharField(
        max_length=50,
        choices=TIPO_EMPRESA_CHOICES,
        blank=True,
        null=True,
        verbose_name="Tipo de Empresa"
    )

    class Meta:
        ordering = ["nome"]
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas"

    def __str__(self):
        if self.funcao and self.sexo:
            titulo = self.funcao.get_abreviacao_por_sexo(self.sexo)
            return f"{titulo} {self.nome}"
        return self.nome

    @property
    def tipo_pessoa(self):
        """Retorna FISICA ou JURIDICA baseado no tipo de documento"""
        if self.tipo_doc == "CPF":
            return "FISICA"
        elif self.tipo_doc == "CNPJ":
            return "JURIDICA"
        else:
            # Passaporte assume pessoa física
            return "FISICA"

    def get_tipo_pessoa_display(self):
        """Retorna o tipo de pessoa formatado para exibição"""
        tipo = self.tipo_pessoa
        return "Pessoa Física" if tipo == "FISICA" else "Pessoa Jurídica"
    
    @property
    def titulo_formatado(self):
        """Retorna o título da função formatado conforme o sexo da pessoa"""
        if self.funcao and self.sexo:
            return self.funcao.get_funcao_por_sexo(self.sexo)
        elif self.funcao:
            return self.funcao.masculino  # Default para masculino se sexo não informado
        return None
    
    @property
    def titulo_abreviado(self):
        """Retorna a abreviação do título conforme o sexo da pessoa"""
        if self.funcao and self.sexo:
            return self.funcao.get_abreviacao_por_sexo(self.sexo)
        elif self.funcao:
            return self.funcao.abreviacao_masculino  # Default para masculino se sexo não informado
        return None
    
    # Propriedades de contato
    @property
    def telefone_principal(self):
        """Retorna o telefone principal da pessoa"""
        return self.telefones.filter(principal=True, ativo=True).first()
    
    @property
    def email_principal(self):
        """Retorna o email principal da pessoa"""
        return self.emails.filter(principal=True, ativo=True).first()
    
    @property
    def telefone_formatado(self):
        """Retorna telefone principal formatado para exibição"""
        telefone = self.telefone_principal
        return telefone.numero_formatado if telefone else None
    
    @property
    def telefone_completo(self):
        """Retorna telefone principal no formato internacional completo"""
        telefone = self.telefone_principal
        return telefone.numero_completo if telefone else None
    
    @property
    def email_str(self):
        """Retorna email principal como string"""
        email = self.email_principal
        return email.email if email else None

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super().save(*args, **kwargs)
