#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('/home/thiago/Projetos/gruporom')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
import boto3
from botocore.exceptions import ClientError

print('=== TESTE DE PERMISSÕES S3 ===')

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)

file_key = 'media/whatsapp/image/2025/08/12/wamid.TEST_1755035157.jpg'

print(f'Bucket: {settings.AWS_STORAGE_BUCKET_NAME}')
print(f'Key: {file_key}')
print(f'Access Key: {settings.AWS_ACCESS_KEY_ID[:10]}...')

# 1. Testa ListObjects
try:
    response = s3_client.list_objects_v2(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Prefix='media/whatsapp/',
        MaxKeys=1
    )
    print('✅ ListObjects: OK')
except ClientError as e:
    print(f'❌ ListObjects: {e}')

# 2. Testa HeadObject
try:
    response = s3_client.head_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=file_key
    )
    print('✅ HeadObject: OK')
except ClientError as e:
    print(f'❌ HeadObject: {e}')

# 3. Testa GetObject diretamente
try:
    response = s3_client.get_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=file_key
    )
    print(f'✅ GetObject: OK (tamanho: {len(response["Body"].read())} bytes)')
except ClientError as e:
    print(f'❌ GetObject: {e}')

# 4. Testa diferentes formatos de URL assinada
try:
    # Formato v2 (antigo)
    signed_url_v2 = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': file_key},
        ExpiresIn=3600,
        HttpMethod='GET'
    )
    print(f'URL v2: {signed_url_v2[:100]}...')
    
    # Formato v4 (novo)
    signed_url_v4 = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': file_key},
        ExpiresIn=3600,
        HttpMethod='GET'
    )
    print(f'URL v4: {signed_url_v4[:100]}...')
    
    # Testa ambas
    import requests
    
    print('\\nTestando URLs:')
    for name, url in [('v2', signed_url_v2), ('v4', signed_url_v4)]:
        try:
            response = requests.get(url, timeout=10)
            print(f'{name}: Status {response.status_code}')
            if response.status_code == 200:
                print(f'  Content-Type: {response.headers.get("content-type")}')
                print(f'  Tamanho: {len(response.content)} bytes')
        except Exception as e:
            print(f'{name}: Erro - {e}')
    
except Exception as e:
    print(f'❌ Erro ao gerar URLs: {e}')

# 5. Verifica bucket policy
try:
    bucket_policy = s3_client.get_bucket_policy(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
    print(f'\\nBucket Policy: {bucket_policy["Policy"][:200]}...')
except ClientError as e:
    if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
        print('\\n⚠️ Nenhuma bucket policy definida')
    else:
        print(f'\\n❌ Erro ao obter bucket policy: {e}')