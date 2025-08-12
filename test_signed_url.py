#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('/home/thiago/Projetos/gruporom')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import WhatsAppMessage
import requests

# Busca a mensagem de Rafael Lima
msg = WhatsAppMessage.objects.get(media_id='media_img_1755035157')

print('=== TESTE URL ASSINADA CORRIGIDA ===')
print(f'URL original: {msg.media_url}')

# Testa o método get_signed_media_url
signed_url = msg.get_signed_media_url()
print(f'URL assinada: {signed_url}')

# Verifica se são diferentes
if signed_url != msg.media_url:
    print('✅ URL assinada foi gerada (diferente da original)')
    
    # Testa se a URL assinada funciona
    try:
        response = requests.head(signed_url, timeout=10)
        print(f'Status da URL assinada: {response.status_code}')
        if response.status_code == 200:
            print('✅ URL assinada funciona!')
        else:
            print('❌ URL assinada não funciona')
    except Exception as e:
        print(f'❌ Erro ao testar URL assinada: {e}')
else:
    print('❌ URL assinada é igual à original (não foi gerada)')