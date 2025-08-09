# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from core.models import Pessoa, Telefone, Email, Pais
from core.choices import TIPO_EMPRESA_CHOICES
from core.utils.validators import validate_documento_pessoa, limpar_documento


class PessoaForm(forms.ModelForm):
    
    class Meta:
        model = Pessoa
        fields = [
            "nome",
            "tipo_doc",
            "doc",
            "nascimento",
            "sexo",
            "funcao",
            "passaporte_numero",
            "passaporte_validade",
            "passaporte_copia",
            "passaporte_nome",
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
            "funcao": forms.Select(attrs={"class": "form-select"}),
            "passaporte_numero": forms.TextInput(attrs={"class": "form-control"}),
            "passaporte_validade": forms.DateInput(
                attrs={"class": "form-control", "type": "date"},
                format="%Y-%m-%d",
            ),
            "passaporte_copia": forms.FileInput(attrs={"class": "form-control"}),
            "passaporte_nome": forms.TextInput(attrs={"class": "form-control"}),
            "endereco": forms.TextInput(attrs={"class": "form-control"}),
            "numero": forms.TextInput(attrs={"class": "form-control"}),
            "complemento": forms.TextInput(attrs={"class": "form-control"}),
            "bairro": forms.TextInput(attrs={"class": "form-control"}),
            "cidade": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.TextInput(
                attrs={"class": "form-control", "maxlength": "2"}
            ),
            "pais": forms.Select(attrs={"class": "form-select"}),
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
            "funcao": "Título",
            "passaporte_numero": "Número do Passaporte",
            "passaporte_validade": "Validade do Passaporte",
            "passaporte_copia": "Cópia do Passaporte",
            "passaporte_nome": "Nome no Passaporte",
            "endereco": "Endereço",
            "numero": "Número",
            "pais": "País",
            "empresa_gruporom": "Empresa do Grupo ROM",
            "tipo_empresa": "Tipo de Empresa",
        }
    
    def clean(self):
        """
        Validação customizada do formulário
        """
        cleaned_data = super().clean()
        documento = cleaned_data.get('doc')
        tipo_doc = cleaned_data.get('tipo_doc')
        
        if documento and tipo_doc:
            try:
                # Validar e limpar documento
                documento_limpo = validate_documento_pessoa(documento, tipo_doc)
                # Salvar documento limpo (sem pontuação)
                cleaned_data['doc'] = documento_limpo
            except ValidationError as e:
                self.add_error('doc', e)
        
        return cleaned_data
    
