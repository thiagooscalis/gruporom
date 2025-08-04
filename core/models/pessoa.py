from django.db import models
from django.utils.text import slugify
from core.choices import TIPO_DOC_CHOICES, SEXO_CHOICES


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
    email = models.EmailField(verbose_name="E-mail")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
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
    pais = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="País"
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

    class Meta:
        ordering = ["nome"]
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas"

    def __str__(self):
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

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super().save(*args, **kwargs)
