# -*- coding: utf-8 -*-
"""
Comando para testar configuração do S3
"""
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import datetime


class Command(BaseCommand):
    help = 'Testa a configuração do S3 fazendo upload de um arquivo de teste'

    def handle(self, *args, **options):
        self.stdout.write("\n🔍 Verificando configuração de storage...")
        
        # Verifica se S3 está habilitado
        use_s3 = getattr(settings, 'USE_S3', False)
        
        if use_s3:
            self.stdout.write(self.style.SUCCESS("✅ S3 está HABILITADO"))
            
            # Mostra configurações (sem mostrar secrets)
            self.stdout.write(f"   Bucket: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'não configurado')}")
            self.stdout.write(f"   Região: {getattr(settings, 'AWS_S3_REGION_NAME', 'não configurado')}")
            
            if hasattr(settings, 'AWS_S3_CUSTOM_DOMAIN') and settings.AWS_S3_CUSTOM_DOMAIN:
                self.stdout.write(f"   CDN: {settings.AWS_S3_CUSTOM_DOMAIN}")
            
            # Testa credenciais
            if not getattr(settings, 'AWS_ACCESS_KEY_ID', None):
                self.stdout.write(self.style.ERROR("❌ AWS_ACCESS_KEY_ID não configurado"))
                return
            
            if not getattr(settings, 'AWS_SECRET_ACCESS_KEY', None):
                self.stdout.write(self.style.ERROR("❌ AWS_SECRET_ACCESS_KEY não configurado"))
                return
                
            self.stdout.write(self.style.SUCCESS("✅ Credenciais configuradas"))
            
        else:
            self.stdout.write(self.style.WARNING("⚠️  S3 está DESABILITADO - usando storage local"))
            self.stdout.write(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
            self.stdout.write(f"   MEDIA_URL: {settings.MEDIA_URL}")
        
        # Testa upload
        self.stdout.write("\n📤 Testando upload de arquivo...")
        
        try:
            # Cria arquivo de teste
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            test_content = f"Teste de upload S3 - {timestamp}\n"
            test_filename = f"test/s3_test_{timestamp}.txt"
            
            # Salva no storage
            path = default_storage.save(
                test_filename,
                ContentFile(test_content.encode())
            )
            
            self.stdout.write(self.style.SUCCESS(f"✅ Upload bem-sucedido: {path}"))
            
            # Obtém URL
            url = default_storage.url(path)
            self.stdout.write(f"   URL: {url}")
            
            # Verifica se arquivo existe
            if default_storage.exists(path):
                self.stdout.write(self.style.SUCCESS("✅ Arquivo verificado no storage"))
                
                # Lê o arquivo de volta
                with default_storage.open(path) as file:
                    content = file.read().decode()
                    if test_content in content:
                        self.stdout.write(self.style.SUCCESS("✅ Conteúdo verificado"))
                    else:
                        self.stdout.write(self.style.ERROR("❌ Conteúdo não corresponde"))
                
                # Remove arquivo de teste
                default_storage.delete(path)
                self.stdout.write(self.style.SUCCESS("✅ Arquivo de teste removido"))
                
            else:
                self.stdout.write(self.style.ERROR("❌ Arquivo não encontrado no storage"))
            
            self.stdout.write(self.style.SUCCESS("\n🎉 Teste concluído com sucesso!"))
            
            if use_s3:
                self.stdout.write(self.style.SUCCESS("   S3 está funcionando corretamente"))
            else:
                self.stdout.write(self.style.WARNING("   Storage local está funcionando"))
                self.stdout.write("   Para usar S3, configure USE_S3=True no .env")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Erro no teste: {e}"))
            
            if use_s3:
                self.stdout.write("\nPossíveis causas:")
                self.stdout.write("1. Credenciais AWS incorretas")
                self.stdout.write("2. Bucket não existe ou sem permissão")
                self.stdout.write("3. Região incorreta")
                self.stdout.write("4. django-storages não instalado (pip install django-storages[s3])")
                
        self.stdout.write("")  # Linha em branco final