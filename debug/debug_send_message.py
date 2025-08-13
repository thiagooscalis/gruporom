#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar envio de mensagem WhatsApp
"""
import os
import django
import requests
import json
import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_send_message():
    """Testa o envio de mensagem via API"""
    
    print("=" * 60)
    print("🧪 TESTE DE ENVIO DE MENSAGEM WHATSAPP")
    print("=" * 60)
    
    # Dados do teste
    conversation_id = 20  # ID de uma conversa existente
    test_message = "Teste de envio via API - " + str(int(time.time()))
    
    print(f"Conversa ID: {conversation_id}")
    print(f"Mensagem: {test_message}")
    print()
    
    # Simula requisição do frontend
    url = "http://localhost:8000/comercial/whatsapp/send-message/"
    
    payload = {
        "conversation_id": conversation_id,
        "message": test_message
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "TestScript/1.0"
    }
    
    try:
        print("📤 Enviando requisição...")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Mensagem enviada com sucesso!")
                print(f"   Message ID: {data.get('message_id')}")
                print(f"   WAMID: {data.get('wamid')}")
                print(f"   Status: {data.get('status')}")
            else:
                print("❌ Erro na resposta:")
                print(f"   Erro: {data.get('error')}")
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Django não está rodando em http://localhost:8000")
        print("   Execute: uv run manage.py runserver")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        
    print()
    print("💡 Para ver o resultado:")
    print("   1. Abra http://localhost:8000/comercial/whatsapp/")
    print("   2. Selecione a conversa testada")
    print("   3. Verifique se a mensagem apareceu com o ícone correto")

if __name__ == "__main__":
    import time
    test_send_message()