# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from core.models import Pessoa, Pais
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
            "email1",
            "email2", 
            "email3",
            "ddi1",
            "ddd1",
            "telefone1",
            "ddi2",
            "ddd2",
            "telefone2",
            "ddi3",
            "ddd3",
            "telefone3",
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
            "email1": forms.EmailInput(attrs={"class": "form-control"}),
            "email2": forms.EmailInput(attrs={"class": "form-control"}),
            "email3": forms.EmailInput(attrs={"class": "form-control"}),
            "ddi1": forms.TextInput(attrs={"class": "form-control", "placeholder": "55"}),
            "ddd1": forms.TextInput(attrs={"class": "form-control", "placeholder": "11"}),
            "telefone1": forms.TextInput(attrs={"class": "form-control"}),
            "ddi2": forms.TextInput(attrs={"class": "form-control", "placeholder": "55"}),
            "ddd2": forms.TextInput(attrs={"class": "form-control", "placeholder": "11"}),
            "telefone2": forms.TextInput(attrs={"class": "form-control"}),
            "ddi3": forms.TextInput(attrs={"class": "form-control", "placeholder": "55"}),
            "ddd3": forms.TextInput(attrs={"class": "form-control", "placeholder": "11"}),
            "telefone3": forms.TextInput(attrs={"class": "form-control"}),
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
        
        # Validar telefone1 (obrigatório) - se algum campo for preenchido, todos devem estar
        ddi1 = cleaned_data.get('ddi1', '').strip() if cleaned_data.get('ddi1') else ''
        ddd1 = cleaned_data.get('ddd1', '').strip() if cleaned_data.get('ddd1') else ''
        telefone1 = cleaned_data.get('telefone1', '').strip() if cleaned_data.get('telefone1') else ''
        
        campos1_preenchidos = sum([bool(ddi1), bool(ddd1), bool(telefone1)])
        
        if 0 < campos1_preenchidos < 3:
            # Se telefone1 tem campos parciais, limpar todos e dar erro
            cleaned_data['ddi1'] = ''
            cleaned_data['ddd1'] = ''
            cleaned_data['telefone1'] = ''
            self.add_error('telefone1', 'Para o telefone principal, todos os campos (DDI, DDD e telefone) devem estar preenchidos.')
        
        # Validar telefones opcionais (2 e 3) - se algum campo estiver faltando, limpar todos
        for i in range(2, 4):  # telefone2, telefone3
            ddi = cleaned_data.get(f'ddi{i}', '').strip() if cleaned_data.get(f'ddi{i}') else ''
            ddd = cleaned_data.get(f'ddd{i}', '').strip() if cleaned_data.get(f'ddd{i}') else ''
            telefone = cleaned_data.get(f'telefone{i}', '').strip() if cleaned_data.get(f'telefone{i}') else ''
            
            # Contar quantos campos estão preenchidos
            campos_preenchidos = sum([bool(ddi), bool(ddd), bool(telefone)])
            
            # Se tem campos parcialmente preenchidos (nem 0 nem 3), limpar todos
            if 0 < campos_preenchidos < 3:
                cleaned_data[f'ddi{i}'] = ''
                cleaned_data[f'ddd{i}'] = ''
                cleaned_data[f'telefone{i}'] = ''
        
        return cleaned_data
    
