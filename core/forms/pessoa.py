# -*- coding: utf-8 -*-
from django import forms
from core.models import Pessoa, Telefone, Email
from core.choices import TIPO_EMPRESA_CHOICES


class PessoaForm(forms.ModelForm):
    # Campos de contato que serão salvos nos models separados
    ddi = forms.CharField(
        max_length=4,
        initial='55',
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "55"}),
        label="DDI",
        help_text="Código do país (ex: 55 para Brasil)"
    )
    
    ddd = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "11"}),
        label="DDD",
        help_text="Código de área"
    )
    
    telefone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "999999999"}),
        label="Telefone"
    )
    
    tipo_telefone = forms.ChoiceField(
        choices=Telefone.TIPO_CHOICES,
        initial='celular',
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Tipo do Telefone"
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "cliente@email.com"}),
        label="E-mail"
    )
    
    tipo_email = forms.ChoiceField(
        choices=Email.TIPO_CHOICES,
        initial='pessoal',
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Tipo do E-mail"
    )
    
    class Meta:
        model = Pessoa
        fields = [
            "nome",
            "tipo_doc",
            "doc",
            "nascimento",
            "sexo",
            "endereco",
            "numero",
            "complemento",
            "bairro",
            "cidade",
            "estado",
            "pais",
            "cep",
            "empresa_gruporom",
            "tipo_empresa",
        ]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "tipo_doc": forms.Select(attrs={"class": "form-select"}),
            "doc": forms.TextInput(attrs={"class": "form-control"}),
            "nascimento": forms.DateInput(
                attrs={"class": "form-control", "type": "date"},
                format="%Y-%m-%d",
            ),
            "sexo": forms.Select(attrs={"class": "form-select"}),
            "endereco": forms.TextInput(attrs={"class": "form-control"}),
            "numero": forms.TextInput(attrs={"class": "form-control"}),
            "complemento": forms.TextInput(attrs={"class": "form-control"}),
            "bairro": forms.TextInput(attrs={"class": "form-control"}),
            "cidade": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.TextInput(
                attrs={"class": "form-control", "maxlength": "2"}
            ),
            "pais": forms.TextInput(attrs={"class": "form-control"}),
            "cep": forms.TextInput(attrs={"class": "form-control"}),
            "empresa_gruporom": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "tipo_empresa": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "tipo_doc": "Tipo de Documento",
            "doc": "Número do Documento",
            "nascimento": "Data de Nascimento",
            "endereco": "Endereço",
            "numero": "Número",
            "pais": "País",
            "empresa_gruporom": "Empresa do Grupo ROM",
            "tipo_empresa": "Tipo de Empresa",
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Se editando uma pessoa existente, pré-preenche os dados de contato
        if self.instance.pk:
            telefone_principal = self.instance.telefone_principal
            if telefone_principal:
                self.fields['ddi'].initial = telefone_principal.ddi
                self.fields['ddd'].initial = telefone_principal.ddd
                self.fields['telefone'].initial = telefone_principal.telefone
                self.fields['tipo_telefone'].initial = telefone_principal.tipo
            
            email_principal = self.instance.email_principal
            if email_principal:
                self.fields['email'].initial = email_principal.email
                self.fields['tipo_email'].initial = email_principal.tipo
    
    def save(self, commit=True):
        # Salva a pessoa primeiro
        pessoa = super().save(commit=commit)
        
        if commit:
            # Dados do telefone
            ddi = self.cleaned_data.get('ddi')
            ddd = self.cleaned_data.get('ddd')
            telefone = self.cleaned_data.get('telefone')
            tipo_telefone = self.cleaned_data.get('tipo_telefone')
            
            # Dados do email
            email = self.cleaned_data.get('email')
            tipo_email = self.cleaned_data.get('tipo_email')
            
            # Salva/atualiza telefone principal
            if ddi and ddd and telefone:
                telefone_obj, created = Telefone.objects.get_or_create(
                    pessoa=pessoa,
                    principal=True,
                    defaults={
                        'ddi': ddi,
                        'ddd': ddd,
                        'telefone': telefone,
                        'tipo': tipo_telefone,
                    }
                )
                if not created:
                    # Atualiza telefone existente
                    telefone_obj.ddi = ddi
                    telefone_obj.ddd = ddd
                    telefone_obj.telefone = telefone
                    telefone_obj.tipo = tipo_telefone
                    telefone_obj.save()
            
            # Salva/atualiza email principal
            if email:
                email_obj, created = Email.objects.get_or_create(
                    pessoa=pessoa,
                    principal=True,
                    defaults={
                        'email': email,
                        'tipo': tipo_email,
                    }
                )
                if not created:
                    # Atualiza email existente
                    email_obj.email = email
                    email_obj.tipo = tipo_email
                    email_obj.save()
        
        return pessoa
