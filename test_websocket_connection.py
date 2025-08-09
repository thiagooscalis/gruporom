#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar conexão WebSocket do WhatsApp Comercial
"""
import asyncio
import websockets
import json
import threading
import time
import requests


async def test_websocket_client():
    """Testa a conexão WebSocket como cliente"""
    uri = "ws://localhost:8000/ws/comercial/whatsapp/"
    
    print(f"🔗 Tentando conectar em {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conexão WebSocket estabelecida!")
            
            # Aguarda mensagens por 30 segundos
            try:
                while True:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    print(f"📨 Mensagem recebida: {message}")
                    
                    # Parse da mensagem
                    try:
                        data = json.loads(message)
                        print(f"📋 Dados: {data}")
                        
                        if data.get('type') == 'conversation_new':
                            print(f"🆕 NOVA CONVERSA: {data.get('conversation', {}).get('id')}")
                            print(f"👤 Cliente: {data.get('conversation', {}).get('contact_name')}")
                            print(f"💬 Mensagem: {data.get('conversation', {}).get('message_preview')}")
                            if 'pending_count' in data:
                                print(f"📊 Conversas pendentes: {data.get('pending_count')}")
                    except json.JSONDecodeError:
                        print(f"⚠️ Mensagem não é JSON válido: {message}")
                        
            except asyncio.TimeoutError:
                print("⏰ Timeout aguardando mensagens")
                
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"🔴 Conexão WebSocket fechada: {e}")
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Erro de status HTTP: {e}")
    except Exception as e:
        print(f"❌ Erro na conexão WebSocket: {e}")


def send_test_webhook():
    """Envia webhook de teste após 5 segundos"""
    print("⏱️  Aguardando 5 segundos antes de enviar webhook...")
    time.sleep(5)
    
    print("📤 Enviando webhook de teste...")
    
    # Dados do webhook de teste
    timestamp = int(time.time())
    client_number = f"5511{timestamp % 100000000:08d}"
    
    webhook_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "5511999999999",
                                "phone_number_id": "PHONE_NUMBER_ID"
                            },
                            "contacts": [
                                {
                                    "profile": {
                                        "name": "Cliente Teste WebSocket"
                                    },
                                    "wa_id": client_number
                                }
                            ],
                            "messages": [
                                {
                                    "from": client_number,
                                    "id": f"wamid.TEST_WS_{timestamp}",
                                    "timestamp": str(timestamp),
                                    "text": {
                                        "body": "🧪 Teste de WebSocket - Esta mensagem deve aparecer em tempo real!"
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
    
    try:
        response = requests.post(
            "http://localhost:8000/webhook/whatsapp/1/",
            json=webhook_payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "WhatsApp/2.0",
            },
            timeout=10
        )
        
        print(f"📊 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Webhook enviado com sucesso!")
            print("🔔 Se o WebSocket estiver funcionando, você deve ver a mensagem acima.")
        else:
            print(f"❌ Erro no webhook: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao enviar webhook: {e}")


async def main():
    """Função principal"""
    print("=" * 60)
    print("🧪 TESTE DE WEBSOCKET - WHATSAPP COMERCIAL")
    print("=" * 60)
    print()
    print("📋 Este script irá:")
    print("   1. Conectar via WebSocket em ws://localhost:8000/ws/comercial/whatsapp/")
    print("   2. Aguardar 5 segundos")
    print("   3. Enviar um webhook de teste")
    print("   4. Verificar se a mensagem WebSocket é recebida")
    print()
    print("⚠️  IMPORTANTE: Certifique-se de que:")
    print("   • Django está rodando em localhost:8000")
    print("   • Redis está ativo")
    print("   • Você tem um usuário do grupo 'Comercial'")
    print()
    
    # Inicia thread para enviar webhook após delay
    webhook_thread = threading.Thread(target=send_test_webhook, daemon=True)
    webhook_thread.start()
    
    # Testa conexão WebSocket
    await test_websocket_client()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")