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
        
        if isinstance(key, str):
            key = key.encode()
        
        self.fernet = Fernet(key)
    
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
        except Exception as e:
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