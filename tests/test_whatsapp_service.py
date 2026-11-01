from app.communication.whatsapp.models import WhatsAppMessage
from app.communication.whatsapp.service import WhatsAppAssistantService


service = WhatsAppAssistantService()


tests = [
    WhatsAppMessage(
        sender="1",
        message="Where is my order?",
        language="en",
    ),
    WhatsAppMessage(
        sender="2",
        message="Je voudrais ma facture",
        language="fr",
    ),
    WhatsAppMessage(
        sender="3",
        message="أريد معرفة سعر المنتج",
        language="ar",
    ),
    WhatsAppMessage(
        sender="4",
        message="میرے آرڈر کی ڈیلیوری کب ہوگی؟",
        language="ur",
    ),
]


for message in tests:
    result = service.process_message(message)

    print(
        message.language,
        "->",
        result.intent,
        "->",
        result.message,
    )


print("Multilingual WhatsApp test successful")