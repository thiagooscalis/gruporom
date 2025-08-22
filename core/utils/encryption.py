# -*- coding: utf-8 -*-
import base64
import os
from cryptography.fernet import Fernet
from django.conf import settings


class FieldEncryption:
    """
    Classe para criptografia de campos sensíveis do banco de dados.
    Utiliza criptografia simétrica com Fernet (AES 128 em modo CBC).
    """
    
    def __init__(self):
        # Obtém a chave do settings ou variável de ambiente
        key = getattr(settings, 'ENCRYPTION_KEY', None)
        if not key:
            key = os.environ.get('DJANGO_ENCRYPTION_KEY')
        
        if not key:
            # Gera uma chave temporária para desenvolvimento (INSEGURO em produção)
            key = Fernet.generate_key()
            print("⚠️  AVISO: Usando chave de criptografia temporária. Configure DJANGO_ENCRYPTION_KEY em produção!")
        else:
            # Se a chave foi fornecida, validar formato
            if isinstance(key, str):
                key = key.strip()  # Remove espaços em branco
                try:
                    # Tenta decodificar para verificar se é válida
                    key_bytes = key.encode('utf-8')
                    # Testa se consegue criar Fernet (isso valida o formato base64)
                    test_fernet = Fernet(key_bytes)
                    key = key_bytes
                except Exception as e:
                    print(f"❌ ERRO: Chave DJANGO_ENCRYPTION_KEY inválida: {str(e)}")
                    print("💡 Gerando nova chave válida:")
                    new_key = Fernet.generate_key().decode()
                    print(f"   DJANGO_ENCRYPTION_KEY={new_key}")
                    print("   ⚠️  Configure esta chave no seu arquivo .env!")
                    key = Fernet.generate_key()
        
        try:
            self.fernet = Fernet(key)
        except Exception as e:
            print(f"❌ ERRO CRÍTICO: Não foi possível inicializar criptografia: {str(e)}")
            # Fallback para chave temporária
            key = Fernet.generate_key()
            self.fernet = Fernet(key)
            print("⚠️  USANDO CHAVE TEMPORÁRIA - DADOS NÃO SERÃO PERSISTENTES!")
    
    def encrypt(self, text):
        """
        Criptografa um texto simples.
        
        Args:
            text (str): Texto a ser criptografado
            
        Returns:
            str: Texto criptografado em base64
        """
        if not text:
            return text
        
        if isinstance(text, str):
            text = text.encode('utf-8')
        
        encrypted = self.fernet.encrypt(text)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_text):
        """
        Descriptografa um texto criptografado.
        
        Args:
            encrypted_text (str): Texto criptografado em base64
            
        Returns:
            str: Texto descriptografado
        """
        if not encrypted_text:
            return encrypted_text
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_text.encode('utf-8'))
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception:
            # Retorna o texto original se não conseguir descriptografar
            # (para compatibilidade com dados existentes)
            return encrypted_text
    
    @staticmethod
    def generate_key():
        """
        Gera uma nova chave de criptografia.
        
        Returns:
            str: Nova chave em base64
        """
        key = Fernet.generate_key()
        return base64.b64encode(key).decode('utf-8')


# Instância global para uso em models
field_encryption = FieldEncryption()