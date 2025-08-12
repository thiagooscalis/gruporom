#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('/home/thiago/Projetos/gruporom')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.storage import default_storage
from django.conf import settings
import boto3

print('=== DEBUG S3 ===')

# Configurações
print(f'Bucket: {settings.AWS_STORAGE_BUCKET_NAME}')
print(f'Region: {settings.AWS_S3_REGION_NAME}')

# Lista arquivos na pasta específica
try:
    files = default_storage.listdir('whatsapp/image/2025/08/12/')
    print(f'Arquivos encontrados: {files[1]}')  # files[1] são os arquivos
    
    # Testa acesso direto via boto3
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    
    # Tenta verificar se o arquivo existe
    file_key = 'media/whatsapp/image/2025/08/12/wamid.TEST_1755035157.jpg'
    print(f'Testando existência da chave: {file_key}')
    
    try:
        response = s3_client.head_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_key
        )
        print(f'✅ Arquivo existe no S3!')
        print(f'Tamanho: {response.get("ContentLength")} bytes')
        print(f'Content-Type: {response.get("ContentType")}')
        
        # Gera URL assinada com acesso direto
        signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': file_key},
            ExpiresIn=3600
        )
        print(f'URL assinada: {signed_url}')
        
        # Testa a URL
        import requests
        response = requests.head(signed_url, timeout=10)
        print(f'Status da URL assinada: {response.status_code}')
        
    except Exception as e:
        print(f'❌ Erro ao verificar arquivo: {e}')
        
        # Lista tudo no bucket para debug
        print('\\nListando primeiros 10 objetos do bucket:')
        response = s3_client.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Prefix='media/whatsapp/',
            MaxKeys=10
        )
        
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f'  - {obj["Key"]}')
        else:
            print('  Nenhum objeto encontrado')
        
except Exception as e:
    print(f'Erro: {e}')