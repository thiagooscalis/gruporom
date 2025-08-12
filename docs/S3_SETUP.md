# Configuração S3 para Mídias do WhatsApp

## 📦 Visão Geral

O sistema está configurado para armazenar todas as mídias do WhatsApp (imagens, vídeos, áudios, documentos) no Amazon S3 ou compatível (CloudFlare R2, DigitalOcean Spaces, etc).

## 🚀 Configuração Rápida

### 1. Instalar Dependências
```bash
# Já incluído no pyproject.toml
pip install django-storages[s3]
```

### 2. Configurar Variáveis de Ambiente

Adicione ao seu arquivo `.env`:

```env
# Habilitar S3
USE_S3=True

# Credenciais AWS
AWS_ACCESS_KEY_ID=sua-access-key
AWS_SECRET_ACCESS_KEY=sua-secret-key

# Configurações do Bucket
AWS_STORAGE_BUCKET_NAME=gruporom-media
AWS_S3_REGION_NAME=us-east-1

# Opcional: CDN customizado
# AWS_S3_CUSTOM_DOMAIN=cdn.seudominio.com
```

### 3. Criar Bucket S3

#### Via AWS Console:
1. Acesse [S3 Console](https://s3.console.aws.amazon.com/)
2. Clique em "Create bucket"
3. Nome: `gruporom-media` (ou o nome escolhido)
4. Região: `us-east-1` (ou sua região preferida)
5. Desmarque "Block all public access" (para arquivos públicos)
6. Criar bucket

#### Via AWS CLI:
```bash
aws s3 mb s3://gruporom-media --region us-east-1
```

### 4. Configurar Política do Bucket

Para permitir leitura pública das mídias:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::gruporom-media/*"
        }
    ]
}
```

### 5. Criar Usuário IAM

1. Acesse [IAM Console](https://console.aws.amazon.com/iam/)
2. Criar novo usuário com acesso programático
3. Anexar política:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": "arn:aws:s3:::gruporom-media"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:PutObjectAcl"
            ],
            "Resource": "arn:aws:s3:::gruporom-media/*"
        }
    ]
}
```

## 🧪 Testar Configuração

```bash
# Teste se o S3 está funcionando
python manage.py test_s3
```

Output esperado:
```
🔍 Verificando configuração de storage...
✅ S3 está HABILITADO
   Bucket: gruporom-media
   Região: us-east-1
✅ Credenciais configuradas

📤 Testando upload de arquivo...
✅ Upload bem-sucedido: test/s3_test_20250107_143022.txt
   URL: https://gruporom-media.s3.us-east-1.amazonaws.com/test/s3_test_20250107_143022.txt
✅ Arquivo verificado no storage
✅ Conteúdo verificado
✅ Arquivo de teste removido

🎉 Teste concluído com sucesso!
   S3 está funcionando corretamente
```

## 📁 Estrutura de Pastas no S3

As mídias são organizadas automaticamente:

```
gruporom-media/
├── whatsapp/
│   ├── image/
│   │   └── 2025/01/07/
│   │       ├── foto1.jpg
│   │       └── foto2.png
│   ├── video/
│   │   └── 2025/01/07/
│   │       └── video1.mp4
│   ├── audio/
│   │   └── 2025/01/07/
│   │       └── audio1.ogg
│   └── document/
│       └── 2025/01/07/
│           ├── arquivo.pdf
│           └── planilha.xlsx
```

## 🔄 Como Funciona

1. **Webhook recebe mensagem** com mídia do WhatsApp
2. **Sistema obtém URL temporária** da mídia (válida por 5 minutos)
3. **Download da mídia** via streaming (limite 25MB)
4. **Upload direto para S3** com metadata
5. **URL S3 salva no banco** para acesso posterior

## 💰 Custos Estimados

Para 10.000 mídias/mês (média 500KB cada):

- **Armazenamento**: ~5GB × $0.023 = $0.12/mês
- **Transferência**: ~5GB × $0.09 = $0.45/mês
- **Requisições**: 10.000 × $0.0004 = $0.04/mês
- **Total**: ~$0.61/mês

## 🛡️ Segurança

### Opção 1: URLs Públicas (Padrão)
- Mídias acessíveis por URL direta
- Ideal para compartilhamento fácil
- URLs não expiram

### Opção 2: URLs Privadas com Assinatura
Para maior segurança, configure no `settings.py`:

```python
AWS_QUERYSTRING_AUTH = True  # Adiciona assinatura nas URLs
AWS_QUERYSTRING_EXPIRE = 3600  # URLs expiram em 1 hora
```

## 🌎 Usando CloudFlare R2 (Alternativa)

CloudFlare R2 é compatível com S3 e não cobra por transferência:

```env
USE_S3=True
AWS_ACCESS_KEY_ID=seu-r2-access-key
AWS_SECRET_ACCESS_KEY=seu-r2-secret-key
AWS_STORAGE_BUCKET_NAME=gruporom-media
AWS_S3_REGION_NAME=auto
AWS_S3_ENDPOINT_URL=https://sua-conta.r2.cloudflarestorage.com
AWS_S3_CUSTOM_DOMAIN=media.seudominio.com  # Se configurar CDN
```

## 🐛 Troubleshooting

### Erro: "Access Denied"
- Verifique as credenciais AWS
- Confirme permissões do usuário IAM
- Verifique nome e região do bucket

### Erro: "Bucket does not exist"
- Confirme o nome exato do bucket
- Verifique a região configurada

### URLs não funcionam
- Verifique política de acesso público do bucket
- Confirme que `AWS_DEFAULT_ACL = None` no settings

### Uploads lentos
- Considere usar uma região mais próxima
- Verifique a conexão de internet do servidor

## 📊 Monitoramento

### CloudWatch Metrics
- Monitore uso de armazenamento
- Acompanhe número de requisições
- Configure alertas de custo

### Logs de Acesso
Configure logging do bucket para auditoria:

```bash
aws s3api put-bucket-logging \
  --bucket gruporom-media \
  --bucket-logging-status file://logging.json
```

## 🔧 Comandos Úteis

```bash
# Listar arquivos no bucket
aws s3 ls s3://gruporom-media/whatsapp/ --recursive

# Sincronizar mídias locais para S3 (migração)
aws s3 sync media/whatsapp/ s3://gruporom-media/whatsapp/

# Fazer backup do bucket
aws s3 sync s3://gruporom-media/ backup/ --delete

# Limpar mídias antigas (> 30 dias)
python manage.py cleanup_old_media
```

## ✅ Checklist de Produção

- [ ] Credenciais AWS configuradas
- [ ] Bucket criado com nome único
- [ ] Política de acesso configurada
- [ ] Usuário IAM com permissões mínimas
- [ ] Teste de upload/download funcionando
- [ ] Backup configurado
- [ ] Monitoramento ativo
- [ ] Budget alerts configurados