from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Token de verificação do Webhook
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "meu_token_secreto")

# Credenciais do WhatsApp API
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")

@app.route("/")
def home():
    return jsonify({"message": "API do Webhook do WhatsApp está rodando!"})

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """
    Verifica a solicitação do webhook para garantir que veio do WhatsApp.
    """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge
    return jsonify({"error": "Token inválido"}), 403

@app.route("/webhook", methods=["POST"])
def receive_whatsapp_webhook():
    """
    Processa mensagens recebidas do WhatsApp e responde automaticamente.
    """
    data = request.get_json()

    if "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                if "messages" in change.get("value", {}):
                    for message in change["value"]["messages"]:
                        user_id = message["from"]

                        # Mensagem automática de resposta
                        response_text = (
                            "Olá! 🎉 Obrigado por entrar em contato. "
                            "Estamos aqui para te ajudar! 😊\n\n"
                            "Se precisar de suporte, envie a palavra *AJUDA*."
                        )

                        # Enviar resposta via WhatsApp
                        send_whatsapp_message(user_id, response_text)

    return jsonify({"status": "Mensagem processada"})

def send_whatsapp_message(to: str, message: str):
    """
    Envia mensagem via WhatsApp Cloud API.
    """
    url = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
