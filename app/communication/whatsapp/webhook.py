from app.communication.whatsapp.client import WhatsAppClient
from app.communication.whatsapp.models import WhatsAppMessage
from app.communication.whatsapp.service import WhatsAppAssistantService


class WhatsAppWebhookHandler:
    def __init__(self):
        self.assistant = WhatsAppAssistantService()
        self.client = WhatsAppClient()

    def handle(self, payload: dict) -> dict:
        try:
            message = (
                payload["entry"][0]
                ["changes"][0]
                ["value"]
                ["messages"][0]
            )

            sender = message["from"]
            text = message["text"]["body"]

        except (KeyError, IndexError, TypeError):
            return {
                "status": "ignored",
                "reason": "No supported text message found",
            }

        incoming = WhatsAppMessage(
            sender=sender,
            message=text,
        )

        reply = self.assistant.process_message(incoming)

        send_result = self.client.send_message(
            recipient=sender,
            message=reply.message,
        )

        return {
            "status": "processed",
            "recipient": sender,
            "intent": reply.intent,
            "reply": reply.message,
            "delivery_status": send_result["status"],
        }