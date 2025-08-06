# -*- coding: utf-8 -*-
from django import forms
from core.models import Pessoa


class PessoaForm(forms.ModelForm):
    class Meta:
        model = Pessoa
        fields = [
            "nome",
            "tipo_doc",
            "doc",
            "email",
            "telefone",
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
        ]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "tipo_doc": forms.Select(attrs={"class": "form-select"}),
            "doc": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefone": forms.TextInput(attrs={"class": "form-control"}),
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
        }
        labels = {
            "tipo_doc": "Tipo de Documento",
            "doc": "Número do Documento",
            "nascimento": "Data de Nascimento",
            "endereco": "Endereço",
            "numero": "Número",
            "pais": "País",
            "empresa_gruporom": "Empresa do Grupo ROM",
        }
