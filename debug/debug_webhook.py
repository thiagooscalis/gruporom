#!/usr/bin/env python
"""
Script para testar o webhook do WhatsApp localmente
"""
import requests
import json

# URL do webhook (substitua pela sua URL do ngrok)
WEBHOOK_URL = "http://localhost:8000/webhook/whatsapp/1/"

# Payload de teste simulando uma mensagem do WhatsApp
test_payload = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "1234567890",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "5511999999999",
                            "phone_number_id": "123456789"
                        },
                        "contacts": [
                            {
                                "profile": {
                                    "name": "Usuário Teste"
                                },
                                "wa_id": "5511988887777"
                            }
                        ],
                        "messages": [
                            {
                                "from": "5511988887777",
                                "id": "wamid.test123",
                                "timestamp": "1640995200",
                                "text": {
                                    "body": "Olá! Esta é uma mensagem de teste."
                                },
                                "type": "text"
                            }
                        ]
                    },
                    "field": "messages"
                }
            ]
        }
    ]
}

def test_webhook():
    print("=== TESTANDO WEBHOOK ===")
    print(f"URL: {WEBHOOK_URL}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\n=== RESPOSTA ===")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ Webhook funcionando!")
        else:
            print(f"\n❌ Erro no webhook: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    test_webhook()