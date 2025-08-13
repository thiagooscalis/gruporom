#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para simular webhook do WhatsApp com clientes únicos
Execute: python simular_webhook.py
"""

import requests
import json
import random
import time
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8000"  # Altere para sua URL em produção
ACCOUNT_ID = 1  # ID da conta WhatsApp


def gerar_cliente_unico():
    """Gera dados únicos para um cliente"""
    timestamp = int(time.time())
    
    # Número único baseado no timestamp
    client_number = f"5511{timestamp % 100000000:08d}"
    
    # Nomes de clientes
    client_names = [
        "Maria Silva", "João Santos", "Ana Costa", "Pedro Oliveira", 
        "Carla Lima", "José Ferreira", "Lucia Pereira", "Carlos Souza", 
        "Rita Almeida", "Marcos Ribeiro", "Fernanda Rocha", "Bruno Alves",
        "Patricia Mendes", "Roberto Costa", "Juliana Dias", "Antônio Pereira",
        "Luciana Santos", "Rafael Lima", "Gabriela Costa", "Thiago Oliveira"
    ]
    client_name = random.choice(client_names)
    
    # Mensagens variadas
    messages = [
        "Olá! Gostaria de informações sobre pacotes de viagem.",
        "Bom dia! Vocês têm promoções para o Nordeste?",
        "Oi! Preciso de um orçamento para lua de mel na Europa.",
        "Olá! Quais são os destinos disponíveis para família?",
        "Boa tarde! Gostaria de saber sobre pacotes para Disney.",
        "Oi! Vocês fazem viagens para o exterior?",
        "Olá! Preciso de informações sobre cruzeiros.",
        "Bom dia! Quero viajar nas férias de julho, têm opções?",
        "Oi! Gostaria de um pacote all inclusive.",
        "Olá! Vocês trabalham com turismo rural?",
        "Boa tarde! Tem algum pacote para Bahia?",
        "Oi! Queria saber preços para Cancún.",
        "Olá! Vocês organizam excursões para grupos?",
        "Bom dia! Gostaria de viajar para a Argentina.",
        "Oi! Tem pacotes para o Chile?",
        "Olá! Quero informações sobre Fernando de Noronha.",
        "Bom dia! Vocês fazem pacotes personalizados?",
        "Oi! Gostaria de um orçamento para Gramado.",
        "Olá! Tem promoção para o Ceará?",
        "Boa tarde! Quero viajar para Portugal."
    ]
    message_text = random.choice(messages)
    
    return {
        'name': client_name,
        'number': client_number,
        'message': message_text,
        'timestamp': timestamp
    }


def criar_payload_webhook(client_data, message_type="text"):
    """Cria o payload JSON para o webhook"""
    message_id = f"wamid.TEST_{client_data['timestamp']}"
    
    # Base do payload
    payload = {
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
                                        "name": client_data['name']
                                    },
                                    "wa_id": client_data['number']
                                }
                            ],
                            "messages": [
                                {
                                    "from": client_data['number'],
                                    "id": message_id,
                                    "timestamp": str(client_data['timestamp']),
                                    "type": message_type
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
    
    # Configura o conteúdo baseado no tipo
    message_obj = payload["entry"][0]["changes"][0]["value"]["messages"][0]
    
    if message_type == "text":
        message_obj["text"] = {
            "body": client_data['message']
        }
    elif message_type == "image":
        message_obj["image"] = {
            "id": f"media_img_{client_data['timestamp']}",
            "mime_type": "image/jpeg",
            "sha256": "fake_sha256_hash_for_image",
            "caption": client_data.get('caption', "Foto enviada pelo cliente")
        }
    elif message_type == "audio":
        message_obj["audio"] = {
            "id": f"media_audio_{client_data['timestamp']}",
            "mime_type": "audio/ogg; codecs=opus",
            "sha256": "fake_sha256_hash_for_audio"
        }
    elif message_type == "video":
        message_obj["video"] = {
            "id": f"media_video_{client_data['timestamp']}",
            "mime_type": "video/mp4",
            "sha256": "fake_sha256_hash_for_video",
            "caption": client_data.get('caption', "Vídeo enviado pelo cliente")
        }
    elif message_type == "document":
        message_obj["document"] = {
            "id": f"media_doc_{client_data['timestamp']}",
            "mime_type": "application/pdf",
            "sha256": "fake_sha256_hash_for_document",
            "filename": client_data.get('filename', "documento.pdf"),
            "caption": client_data.get('caption', "Documento enviado pelo cliente")
        }
    
    return payload


def escolher_tipo_mensagem():
    """Permite ao usuário escolher o tipo de mensagem"""
    print("📱 Tipos de mensagem disponíveis:")
    print("1. Texto (padrão)")
    print("2. Imagem com legenda")
    print("3. Áudio")
    print("4. Vídeo com legenda")
    print("5. Documento PDF")
    print()
    
    while True:
        try:
            opcao = input("Escolha o tipo (1-5) [1]: ").strip()
            if opcao == "" or opcao == "1":
                return "text", {}
            elif opcao == "2":
                caption = input("Digite a legenda da imagem: ").strip()
                return "image", {"caption": caption if caption else "Foto enviada pelo cliente"}
            elif opcao == "3":
                return "audio", {}
            elif opcao == "4":
                caption = input("Digite a legenda do vídeo: ").strip()
                return "video", {"caption": caption if caption else "Vídeo enviado pelo cliente"}
            elif opcao == "5":
                filename = input("Nome do arquivo [documento.pdf]: ").strip()
                caption = input("Digite a legenda do documento: ").strip()
                return "document", {
                    "filename": filename if filename else "documento.pdf",
                    "caption": caption if caption else "Documento enviado pelo cliente"
                }
            else:
                print("Opção inválida. Digite um número de 1 a 5.")
        except KeyboardInterrupt:
            print("\n❌ Cancelado")
            exit()


def enviar_webhook():
    """Envia webhook simulado para o sistema"""
    # Escolhe tipo de mensagem
    message_type, extra_data = escolher_tipo_mensagem()
    
    # Gera cliente único
    client_data = gerar_cliente_unico()
    client_data.update(extra_data)  # Adiciona dados extras (caption, filename, etc.)
    
    print(f"\n👤 Cliente gerado: {client_data['name']} ({client_data['number']})")
    
    if message_type == "text":
        print(f"💬 Mensagem: {client_data['message']}")
    elif message_type == "image":
        print(f"📷 Imagem: {client_data.get('caption', 'Foto enviada pelo cliente')}")
    elif message_type == "audio":
        print(f"🎵 Áudio enviado")
    elif message_type == "video":
        print(f"🎥 Vídeo: {client_data.get('caption', 'Vídeo enviado pelo cliente')}")
    elif message_type == "document":
        print(f"📄 Documento: {client_data.get('filename', 'documento.pdf')}")
        if client_data.get('caption'):
            print(f"    Legenda: {client_data['caption']}")
    print()

    # Cria payload
    webhook_payload = criar_payload_webhook(client_data, message_type)
    
    url = f"{BASE_URL}/webhook/whatsapp/{ACCOUNT_ID}/"

    print(f"📤 Enviando webhook para: {url}")
    print()

    try:
        # Envia POST com o payload
        response = requests.post(
            url,
            json=webhook_payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "WhatsApp/2.0",
            },
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Webhook enviado com sucesso!")
            print()
            print("🔍 Verifique agora:")
            print(f"1. Página de debug: {BASE_URL}/administracao/whatsapp/account/{ACCOUNT_ID}/debug/")
            print(f"2. Fila comercial: {BASE_URL}/comercial/whatsapp/")
            print()
            print("📊 Para verificar no banco:")
            print('python manage.py shell -c "from core.models import WhatsAppMessage, WhatsAppConversation; print(f\'Mensagens: {WhatsAppMessage.objects.count()}\'); print(f\'Conversas pendentes: {WhatsAppConversation.objects.filter(status=\\"pending\\").count()}\')"')
            print()
            print("🔔 Se estiver com a página comercial aberta, você deve receber:")
            print("   • Notificação WebSocket em tempo real")
            print("   • Som de notificação")
            print("   • Atualização do contador")
        else:
            print(f"❌ Erro: Status {response.status_code}")
            print(f"Resposta: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print(f"Verifique se o Django está rodando em {BASE_URL}")
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 SIMULADOR DE WEBHOOK WHATSAPP")
    print("=" * 60)
    print()

    print(f"Servidor: {BASE_URL}")
    print(f"Account ID: {ACCOUNT_ID}")
    print()
    
    print("📋 O que este script faz:")
    print("   • Gera um cliente único com nome e número aleatórios")
    print("   • Permite escolher tipo de mensagem (texto, imagem, áudio, vídeo, documento)")
    print("   • Envia webhook simulado do WhatsApp com mídia ou texto")
    print("   • Cria nova conversa pendente na fila comercial")
    print("   • Testa o download automático de mídias para S3")
    print("   • Dispara notificação WebSocket em tempo real")
    print()

    resposta = input("Deseja enviar o webhook simulado? (s/N): ")

    if resposta.lower() == "s":
        print()
        enviar_webhook()
    else:
        print("❌ Cancelado")
