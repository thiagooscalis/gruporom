# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import Group
from django.db import models
from core.models import Usuario, Pessoa


class UsuarioForm(forms.ModelForm):
    # Campo para seleção de pessoa com autocomplete
    pessoa = forms.ModelChoiceField(
        queryset=Pessoa.objects.none(),  # Vazio por padrão
        required=True,
        widget=forms.HiddenInput(),
        help_text="Digite para buscar uma pessoa disponível"
    )
    
    # Campo de busca para autocomplete
    pessoa_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o nome, documento ou email da pessoa...',
            'autocomplete': 'off'
        }),
        label="Buscar Pessoa"
    )
    
    # Campo para grupos
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
        label="Grupos de Acesso",
        error_messages={'required': 'Selecione pelo menos um grupo de acesso.'}
    )
    
    # Campos de senha
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Senha",
        required=False,
        help_text="Deixe em branco para manter a senha atual (apenas na edição)"
    )
    
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirmar Senha",
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['pessoa', 'pessoa_search', 'username', 'is_active', 'is_staff', 'groups']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'username': 'Nome de Usuário',
            'is_active': 'Usuário Ativo',
            'is_staff': 'Acesso ao Admin Django',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Se for edição, pré-preenche o campo de busca e pessoa selecionada
        if self.instance.pk:
            self.fields['pessoa'].queryset = Pessoa.objects.filter(pk=self.instance.pessoa.pk)
            self.fields['pessoa_search'].initial = f"{self.instance.pessoa.nome} - {self.instance.pessoa.doc}"
            # Senha não é obrigatória na edição
            self.fields['password'].help_text = "Deixe em branco para manter a senha atual"
        else:
            # Senha é obrigatória na criação
            self.fields['password'].required = True
            self.fields['password_confirm'].required = True
            self.fields['password'].help_text = "Mínimo 8 caracteres"
    
    def clean_pessoa(self):
        """Valida o campo pessoa"""
        pessoa_id = self.data.get('pessoa')
        if pessoa_id:
            try:
                pessoa = Pessoa.objects.get(pk=pessoa_id)
                # Verifica se a pessoa já tem usuário (exceto no caso de edição)
                if pessoa.usuario and (not self.instance.pk or pessoa.usuario.pk != self.instance.pk):
                    raise forms.ValidationError("Esta pessoa já possui um usuário vinculado.")
                return pessoa
            except Pessoa.DoesNotExist:
                raise forms.ValidationError("Pessoa inválida.")
        else:
            raise forms.ValidationError("Selecione uma pessoa.")
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        groups = cleaned_data.get('groups')
        
        # Valida se pelo menos um grupo foi selecionado
        if not groups:
            raise forms.ValidationError("Selecione pelo menos um grupo de acesso.")
        
        # Valida senhas apenas se foram fornecidas
        if password or password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("As senhas não coincidem.")
            
            if len(password) < 8:
                raise forms.ValidationError("A senha deve ter pelo menos 8 caracteres.")
        
        # Se for criação, senha é obrigatória
        if not self.instance.pk and not password:
            raise forms.ValidationError("Senha é obrigatória para novos usuários.")
        
        return cleaned_data
    
    def save(self, commit=True):
        usuario = super().save(commit=False)
        
        # Define senha se foi fornecida
        password = self.cleaned_data.get('password')
        if password:
            usuario.set_password(password)
        
        if commit:
            usuario.save()
            self.save_m2m()  # Salva relacionamentos many-to-many (grupos)
        
        return usuario