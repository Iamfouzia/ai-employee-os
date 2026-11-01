from app.communication.whatsapp.webhook import WhatsAppWebhookHandler


payload = {
    "entry": [
        {
            "changes": [
                {
                    "value": {
                        "messages": [
                            {
                                "from": "923001234567",
                                "type": "text",
                                "text": {
                                    "body": "Where is my order?"
                                },
                            }
                        ]
                    }
                }
            ]
        }
    ]
}


handler = WhatsAppWebhookHandler()

result = handler.handle(payload)

print("WhatsApp webhook successful")
print(result)