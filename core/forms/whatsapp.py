# -*- coding: utf-8 -*-
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Button, HTML
from crispy_forms.bootstrap import FormActions
from core.models import WhatsAppAccount, WhatsAppTemplate, Usuario


class WhatsAppAccountForm(forms.ModelForm):
    """
    Formulário para criar/editar contas WhatsApp
    """
    
    class Meta:
        model = WhatsAppAccount
        fields = [
            'name',
            'phone_number',
            'phone_number_id',
            'business_account_id',
            'app_id',
            'app_secret',
            'access_token',
            'webhook_verify_token',
            'responsavel',
            'status',
            'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Grupo ROM - Atendimento'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+5511999999999',
                'pattern': r'\+[1-9]\d{1,14}',
                'title': 'Número no formato internacional (+5511999999999)'
            }),
            'phone_number_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123456789012345'
            }),
            'business_account_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '987654321098765'
            }),
            'app_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1234567890123456'
            }),
            'app_secret': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Chave secreta do aplicativo Facebook'
            }),
            'access_token': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Token de acesso permanente da API do WhatsApp Business'
            }),
            'webhook_verify_token': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Token para verificação do webhook'
            }),
            'responsavel': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        help_texts = {
            'name': 'Nome identificador da conta para uso interno',
            'phone_number': 'Número no formato internacional (+5511999999999)',
            'phone_number_id': 'ID do número obtido na configuração da API',
            'business_account_id': 'ID da conta de negócios do WhatsApp',
            'app_id': 'ID do aplicativo criado no Facebook for Developers',
            'app_secret': 'Chave secreta do aplicativo (App Secret)',
            'access_token': 'Token permanente gerado no Facebook for Developers',
            'webhook_verify_token': 'Token personalizado para verificação do webhook',
            'responsavel': 'Usuário responsável pela conta',
            'status': 'Status atual da conta na API do WhatsApp',
            'is_active': 'Desmarque para desativar temporariamente a conta',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtra apenas usuários ativos para responsavel
        self.fields['responsavel'].queryset = Usuario.objects.filter(is_active=True)
        
        # Configuração do Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': True}
        
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-8'),
                Column('is_active', css_class='col-md-4 d-flex align-items-center justify-content-center'),
            ),
            Row(
                Column('phone_number', css_class='col-md-6'),
                Column('status', css_class='col-md-6'),
            ),
            Row(
                Column('phone_number_id', css_class='col-md-6'),
                Column('business_account_id', css_class='col-md-6'),
            ),
            'access_token',
            Row(
                Column('webhook_verify_token', css_class='col-md-8'),
                Column('responsavel', css_class='col-md-4'),
            ),
        )
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Remove espaços e caracteres especiais, exceto +
            phone_number = ''.join(c for c in phone_number if c.isdigit() or c == '+')
            
            # Valida formato internacional
            if not phone_number.startswith('+'):
                raise forms.ValidationError('Número deve começar com +')
            
            if len(phone_number) < 8 or len(phone_number) > 16:
                raise forms.ValidationError('Número deve ter entre 8 e 16 dígitos')
        
        return phone_number
    
    def clean_access_token(self):
        access_token = self.cleaned_data.get('access_token')
        if access_token:
            access_token = access_token.strip()
            if len(access_token) < 50:
                raise forms.ValidationError('Token de acesso parece ser muito curto')
        return access_token
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validações adicionais
        phone_number = cleaned_data.get('phone_number')
        phone_number_id = cleaned_data.get('phone_number_id')
        
        if phone_number and phone_number_id:
            # Verifica se já existe outra conta com o mesmo número
            existing_account = WhatsAppAccount.objects.filter(
                phone_number=phone_number
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_account.exists():
                raise forms.ValidationError({
                    'phone_number': 'Já existe uma conta com este número de telefone'
                })
            
            # Verifica phone_number_id único
            existing_phone_id = WhatsAppAccount.objects.filter(
                phone_number_id=phone_number_id
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_phone_id.exists():
                raise forms.ValidationError({
                    'phone_number_id': 'Já existe uma conta com este Phone Number ID'
                })
        
        return cleaned_data


class WhatsAppAccountTestForm(forms.Form):
    """
    Formulário para testar conectividade da conta WhatsApp usando templates
    """
    
    test_phone_number = forms.CharField(
        label='Número para Teste',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+5511999999999',
            'pattern': r'\+[1-9]\d{1,14}'
        }),
        help_text='Número no formato internacional para enviar mensagem de teste'
    )
    
    template = forms.ModelChoiceField(
        queryset=WhatsAppTemplate.objects.none(),
        label='Template de Mensagem',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='Selecione um template aprovado para enviar',
        empty_label='Selecione um template...'
    )
    
    # Campos dinâmicos para variáveis do template serão adicionados via JavaScript
    
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)
        super().__init__(*args, **kwargs)
        
        # Filtra apenas templates aprovados da conta
        if self.account:
            self.fields['template'].queryset = WhatsAppTemplate.objects.filter(
                account=self.account,
                status='approved',
                is_active=True
            )
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'test_phone_number',
            'template',
            FormActions(
                Submit('test_connection', 'Enviar Teste', css_class='btn btn-warning'),
                Button('cancel', 'Cancelar', css_class='btn btn-secondary', onclick='$("#testModal").modal("hide");')
            )
        )
    
    def clean_test_phone_number(self):
        phone_number = self.cleaned_data.get('test_phone_number')
        if phone_number:
            # Remove espaços e caracteres especiais, exceto +
            phone_number = ''.join(c for c in phone_number if c.isdigit() or c == '+')
            
            if not phone_number.startswith('+'):
                raise forms.ValidationError('Número deve começar com +')
            
            if len(phone_number) < 8 or len(phone_number) > 16:
                raise forms.ValidationError('Número deve ter entre 8 e 16 dígitos')
        
        return phone_number


class WhatsAppTemplateForm(forms.ModelForm):
    """
    Formulário para criar/editar templates do WhatsApp
    """
    
    # Campos dinâmicos para exemplos de variáveis
    variable_1 = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Exemplo: João Silva'
        }),
        label='Exemplo para {{1}}'
    )
    
    variable_2 = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Exemplo: Grupo ROM'
        }),
        label='Exemplo para {{2}}'
    )
    
    variable_3 = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Exemplo: 12345'
        }),
        label='Exemplo para {{3}}'
    )
    
    variable_4 = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Exemplo: 10/01/2025'
        }),
        label='Exemplo para {{4}}'
    )
    
    variable_5 = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Exemplo: 14:30'
        }),
        label='Exemplo para {{5}}'
    )
    
    class Meta:
        model = WhatsAppTemplate
        fields = [
            'account',
            'name',
            'display_name',
            'category',
            'language',
            'header_text',
            'body_text',
            'footer_text',
            'has_buttons',
            'is_active',
        ]
        widgets = {
            'account': forms.Select(attrs={
                'class': 'form-select'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'exemplo_template_promocao',
                'pattern': r'^[a-z0-9_]+$',
                'title': 'Apenas letras minúsculas, números e underscore'
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Template de Promoção'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'language': forms.Select(attrs={
                'class': 'form-select'
            }),
            'header_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cabeçalho do template (máx. 60 caracteres)',
                'maxlength': 60
            }),
            'body_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Olá {{1}}! Temos uma oferta especial para você: {{2}}',
                'maxlength': 1024
            }),
            'footer_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rodapé do template (máx. 60 caracteres)',
                'maxlength': 60
            }),
            'has_buttons': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        help_texts = {
            'name': 'Nome técnico do template (apenas letras minúsculas, números e _)',
            'display_name': 'Nome amigável para exibição na interface',
            'category': 'Categoria do template conforme WhatsApp Business API',
            'language': 'Idioma do template',
            'header_text': 'Texto do cabeçalho (opcional, máximo 60 caracteres)',
            'body_text': 'Texto principal. Use {{1}}, {{2}}, etc. para variáveis',
            'footer_text': 'Texto do rodapé (opcional, máximo 60 caracteres)',
            'has_buttons': 'Marque se o template terá botões de ação',
            'is_active': 'Template ativo para uso'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtra apenas contas ativas
        self.fields['account'].queryset = WhatsAppAccount.objects.filter(is_active=True)
        
        # Se for edição, desabilita campos que não podem ser alterados após aprovação
        if self.instance and self.instance.pk and self.instance.status == 'approved':
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['category'].widget.attrs['disabled'] = True
            self.fields['language'].widget.attrs['disabled'] = True
        
        # Configuração do Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': True}
        
        self.helper.layout = Layout(
            Row(
                Column('account', css_class='col-md-6'),
                Column('category', css_class='col-md-6'),
            ),
            Row(
                Column('name', css_class='col-md-6'),
                Column('language', css_class='col-md-6'),
            ),
            'display_name',
            'header_text',
            'body_text',
            'footer_text',
            # Seção de exemplos de variáveis
            HTML('<hr><h6 class="text-muted mb-3"><i class="fas fa-tags me-2"></i>Exemplos das Variáveis</h6>'),
            HTML('<div id="variable-examples-section">'),
            Row(
                Column('variable_1', css_class='col-md-6 variable-field', css_id='field-variable-1'),
                Column('variable_2', css_class='col-md-6 variable-field', css_id='field-variable-2'),
            ),
            Row(
                Column('variable_3', css_class='col-md-6 variable-field', css_id='field-variable-3'),
                Column('variable_4', css_class='col-md-6 variable-field', css_id='field-variable-4'),
            ),
            Row(
                Column('variable_5', css_class='col-md-6 variable-field', css_id='field-variable-5'),
            ),
            HTML('</div>'),
            HTML('<small class="text-muted">💡 Preencha apenas os exemplos das variáveis que você usar no template ({{1}}, {{2}}, etc.)</small>'),
            Row(
                Column('has_buttons', css_class='col-md-6 d-flex align-items-center'),
                Column('is_active', css_class='col-md-6 d-flex align-items-center'),
            ),
        )
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.lower().strip()
            
            # Valida formato
            import re
            if not re.match(r'^[a-z0-9_]+$', name):
                raise forms.ValidationError(
                    'Nome deve conter apenas letras minúsculas, números e underscore'
                )
            
            # Valida comprimento
            if len(name) < 3:
                raise forms.ValidationError('Nome deve ter pelo menos 3 caracteres')
            
            if len(name) > 512:
                raise forms.ValidationError('Nome deve ter no máximo 512 caracteres')
            
            # Verifica unicidade por conta e idioma
            account = self.cleaned_data.get('account')
            language = self.cleaned_data.get('language')
            
            if account and language:
                existing = WhatsAppTemplate.objects.filter(
                    account=account,
                    name=name,
                    language=language
                ).exclude(pk=self.instance.pk if self.instance else None)
                
                if existing.exists():
                    raise forms.ValidationError(
                        'Já existe um template com este nome nesta conta e idioma'
                    )
        
        return name
    
    def clean_body_text(self):
        body_text = self.cleaned_data.get('body_text')
        if body_text:
            body_text = body_text.strip()
            
            # Valida variáveis
            import re
            variables = re.findall(r'\{\{(\d+)\}\}', body_text)
            
            if variables:
                # Converte para inteiros e ordena
                var_numbers = sorted([int(v) for v in variables])
                
                # Verifica se são sequenciais começando de 1
                if var_numbers != list(range(1, len(var_numbers) + 1)):
                    raise forms.ValidationError(
                        'Variáveis devem ser sequenciais começando de {{1}}. '
                        f'Encontradas: {", ".join([f"{{{{{v}}}}}" for v in var_numbers])}'
                    )
                
                # Limite de variáveis
                if len(var_numbers) > 10:
                    raise forms.ValidationError('Máximo de 10 variáveis permitidas')
        
        return body_text
    
    def clean_header_text(self):
        header_text = self.cleaned_data.get('header_text')
        if header_text:
            header_text = header_text.strip()
            if len(header_text) > 60:
                raise forms.ValidationError('Cabeçalho deve ter no máximo 60 caracteres')
        return header_text
    
    def clean_footer_text(self):
        footer_text = self.cleaned_data.get('footer_text')
        if footer_text:
            footer_text = footer_text.strip()
            if len(footer_text) > 60:
                raise forms.ValidationError('Rodapé deve ter no máximo 60 caracteres')
        return footer_text
    
    def save(self, commit=True):
        template = super().save(commit=False)
        
        # Define o usuário criador
        if not template.pk and self.user:
            template.criado_por = self.user
        
        # Salva exemplos das variáveis se fornecidos
        examples = {}
        for i in range(1, 6):  # variáveis 1 a 5
            var_value = self.cleaned_data.get(f'variable_{i}')
            if var_value and var_value.strip():
                examples[str(i)] = var_value.strip()
        
        if examples:
            template.variables_examples = examples
        
        if commit:
            template.save()
        
        return template
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtra apenas contas ativas
        self.fields['account'].queryset = WhatsAppAccount.objects.filter(is_active=True)
        
        # Se for edição, desabilita campos que não podem ser alterados após aprovação
        if self.instance and self.instance.pk and self.instance.status == 'approved':
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['category'].widget.attrs['disabled'] = True
            self.fields['language'].widget.attrs['disabled'] = True
        
        # Se está editando, preenche os campos de variáveis
        if self.instance and self.instance.pk and self.instance.variables_examples:
            for var_num, example in self.instance.variables_examples.items():
                field_name = f'variable_{var_num}'
                if field_name in self.fields:
                    self.fields[field_name].initial = example
        
        # Configuração do Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': True}
        
        self.helper.layout = Layout(
            Row(
                Column('account', css_class='col-md-6'),
                Column('category', css_class='col-md-6'),
            ),
            Row(
                Column('name', css_class='col-md-6'),
                Column('language', css_class='col-md-6'),
            ),
            'display_name',
            'header_text',
            'body_text',
            'footer_text',
            # Seção de exemplos de variáveis
            HTML('<hr><h6 class="text-muted mb-3"><i class="fas fa-tags me-2"></i>Exemplos das Variáveis</h6>'),
            HTML('<div id="variable-examples-section">'),
            Row(
                Column('variable_1', css_class='col-md-6 variable-field', css_id='field-variable-1'),
                Column('variable_2', css_class='col-md-6 variable-field', css_id='field-variable-2'),
            ),
            Row(
                Column('variable_3', css_class='col-md-6 variable-field', css_id='field-variable-3'),
                Column('variable_4', css_class='col-md-6 variable-field', css_id='field-variable-4'),
            ),
            Row(
                Column('variable_5', css_class='col-md-6 variable-field', css_id='field-variable-5'),
            ),
            HTML('</div>'),
            HTML('<small class="text-muted">💡 Preencha apenas os exemplos das variáveis que você usar no template ({{1}}, {{2}}, etc.)</small>'),
            Row(
                Column('has_buttons', css_class='col-md-6 d-flex align-items-center'),
                Column('is_active', css_class='col-md-6 d-flex align-items-center'),
            ),
        )