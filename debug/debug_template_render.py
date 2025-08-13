#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('/home/thiago/Projetos/gruporom')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.template.loader import render_to_string
from core.models import WhatsAppMessage

# Busca a mensagem de Rafael Lima
msg = WhatsAppMessage.objects.get(media_id='media_img_1755035157')

print('=== DEBUG TEMPLATE RENDER ===')
print(f'Mensagem ID: {msg.id}')
print(f'Is Media: {msg.is_media}')
print(f'Media URL: {msg.media_url}')
print(f'Message Type: {msg.message_type}')

# Testa get_signed_media_url
signed_url = msg.get_signed_media_url()
print(f'Signed URL: {signed_url}')
print(f'URLs diferentes: {signed_url != msg.media_url}')

print('\n=== RENDERIZAÇÃO DO TEMPLATE ===')
try:
    html = render_to_string('comercial/whatsapp/partials/message_item.html', {'message': msg})
    
    # Busca por elementos específicos
    lines = html.split('\n')
    for i, line in enumerate(lines):
        line_clean = line.strip()
        if ('media-image' in line_clean or 
            'img src' in line_clean or 
            'DEBUG:' in line_clean or
            'Mídia não carregada' in line_clean):
            print(f'{i:3d}: {line}')
    
    # Verifica se contém elementos esperados
    checks = {
        'has_debug_comment': 'DEBUG:' in html,
        'has_media_image_class': 'media-image' in html,
        'has_img_tag': '<img' in html,
        'has_signed_url': signed_url in html if signed_url else False,
        'has_pending_media': 'Mídia não carregada' in html,
        'has_media_url': msg.media_url in html
    }
    
    print('\n=== VERIFICAÇÕES ===')
    for check, result in checks.items():
        status = '✅' if result else '❌'
        print(f'{status} {check}: {result}')

except Exception as e:
    print(f'❌ Erro ao renderizar template: {e}')
    import traceback
    traceback.print_exc()