# Generated manually
from django.db import migrations
from django.conf import settings
import os


def encrypt_existing_tokens(apps, schema_editor):
    """
    Criptografa tokens existentes no banco de dados
    """
    # Import aqui para evitar problemas de circular import
    from core.utils.encryption import field_encryption
    
    WhatsAppAccount = apps.get_model('core', 'WhatsAppAccount')
    
    # Atualiza todas as contas existentes
    for account in WhatsAppAccount.objects.all():
        needs_update = False
        
        # Criptografa app_secret se existir e não estiver criptografado
        if account.app_secret and not account.app_secret.startswith('gAAAAA'):  # Padrão do Fernet
            try:
                account.app_secret = field_encryption.encrypt(account.app_secret)
                needs_update = True
            except Exception:
                pass  # Mantém o valor original se falhar
        
        # Criptografa access_token se existir e não estiver criptografado  
        if account.access_token and not account.access_token.startswith('gAAAAA'):
            try:
                account.access_token = field_encryption.encrypt(account.access_token)
                needs_update = True
            except Exception:
                pass
        
        # Criptografa webhook_verify_token se existir e não estiver criptografado
        if account.webhook_verify_token and not account.webhook_verify_token.startswith('gAAAAA'):
            try:
                account.webhook_verify_token = field_encryption.encrypt(account.webhook_verify_token)
                needs_update = True
            except Exception:
                pass
        
        if needs_update:
            account.save(update_fields=['app_secret', 'access_token', 'webhook_verify_token', 'atualizado_em'])


def decrypt_tokens(apps, schema_editor):
    """
    Descriptografa tokens (migração reversa)
    """
    from core.utils.encryption import field_encryption
    
    WhatsAppAccount = apps.get_model('core', 'WhatsAppAccount')
    
    for account in WhatsAppAccount.objects.all():
        needs_update = False
        
        if account.app_secret:
            try:
                account.app_secret = field_encryption.decrypt(account.app_secret)
                needs_update = True
            except Exception:
                pass
        
        if account.access_token:
            try:
                account.access_token = field_encryption.decrypt(account.access_token)
                needs_update = True
            except Exception:
                pass
        
        if account.webhook_verify_token:
            try:
                account.webhook_verify_token = field_encryption.decrypt(account.webhook_verify_token)
                needs_update = True
            except Exception:
                pass
        
        if needs_update:
            account.save(update_fields=['app_secret', 'access_token', 'webhook_verify_token', 'atualizado_em'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_alter_whatsappaccount_access_token_and_more'),
    ]

    operations = [
        migrations.RunPython(
            encrypt_existing_tokens,
            decrypt_tokens,
            elidable=True,
        ),
    ]