from django.contrib.auth.forms import PasswordChangeForm


class AlterarSenhaForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configuração dos campos
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Digite sua senha atual'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Digite a nova senha'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme a nova senha'
        })
        
        # Labels em português
        self.fields['old_password'].label = 'Senha Atual'
        self.fields['new_password1'].label = 'Nova Senha'
        self.fields['new_password2'].label = 'Confirmar Nova Senha'