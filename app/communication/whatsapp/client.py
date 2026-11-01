class WhatsAppClient:
    """
    Development WhatsApp client.

    Simulates sending messages while external provider
    credentials are unavailable.

    Later this class can be replaced with Meta, Twilio,
    Vonage, or another WhatsApp Business provider.
    """

    def send_message(
        self,
        recipient: str,
        message: str,
    ) -> dict:

        print()
        print("========== WHATSAPP OUTBOUND ==========")
        print("To:", recipient)
        print("Message:", message)
        print("=======================================")
        print()

        return {
            "status": "sent_mock",
            "recipient": recipient,
            "message": message,
        }