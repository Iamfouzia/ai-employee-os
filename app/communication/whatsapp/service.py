from app.communication.whatsapp.models import (
    WhatsAppMessage,
    WhatsAppReply,
)


class WhatsAppAssistantService:
    SUPPORTED_LANGUAGES = {"en", "fr", "ar", "ur"}

    KEYWORDS = {
        "order_support": {
            "en": ["order", "delivery", "tracking", "shipment"],
            "fr": ["commande", "livraison", "suivi", "colis"],
            "ar": ["طلب", "توصيل", "شحنة", "تتبع"],
            "ur": ["آرڈر", "ڈیلیوری", "ترسیل", "ٹریک"],
        },
        "billing": {
            "en": ["invoice", "receipt", "payment", "billing"],
            "fr": ["facture", "reçu", "paiement"],
            "ar": ["فاتورة", "إيصال", "دفع"],
            "ur": ["انوائس", "رسید", "ادائیگی"],
        },
        "product_recommendation": {
            "en": ["price", "product", "recommend", "recommendation"],
            "fr": ["prix", "produit", "recommande", "recommandation"],
            "ar": ["سعر", "منتج", "اقترح", "توصية"],
            "ur": ["قیمت", "پروڈکٹ", "تجویز"],
        },
    }

    REPLIES = {
        "en": {
            "order_support":
                "I can help with your order. Please provide your order number.",
            "billing":
                "I can help with your invoice or payment. Please provide your order or invoice number.",
            "product_recommendation":
                "I can help you choose a product. Tell me what you are looking for and your budget.",
            "general_support":
                "How can I help you today?",
        },
        "fr": {
            "order_support":
                "Je peux vous aider avec votre commande. Veuillez fournir votre numéro de commande.",
            "billing":
                "Je peux vous aider avec votre facture ou votre paiement. Veuillez fournir votre numéro de commande ou de facture.",
            "product_recommendation":
                "Je peux vous aider à choisir un produit. Indiquez-moi ce que vous recherchez et votre budget.",
            "general_support":
                "Comment puis-je vous aider aujourd'hui ?",
        },
        "ar": {
            "order_support":
                "يمكنني مساعدتك بخصوص طلبك. يرجى إرسال رقم الطلب.",
            "billing":
                "يمكنني مساعدتك بخصوص الفاتورة أو الدفع. يرجى إرسال رقم الطلب أو الفاتورة.",
            "product_recommendation":
                "يمكنني مساعدتك في اختيار المنتج المناسب. أخبرني بما تبحث عنه وميزانيتك.",
            "general_support":
                "كيف يمكنني مساعدتك اليوم؟",
        },
        "ur": {
            "order_support":
                "میں آپ کے آرڈر میں مدد کر سکتا ہوں۔ براہ کرم اپنا آرڈر نمبر فراہم کریں۔",
            "billing":
                "میں انوائس یا ادائیگی میں مدد کر سکتا ہوں۔ براہ کرم آرڈر یا انوائس نمبر فراہم کریں۔",
            "product_recommendation":
                "میں مناسب پروڈکٹ منتخب کرنے میں مدد کر سکتا ہوں۔ اپنی ضرورت اور بجٹ بتائیں۔",
            "general_support":
                "آج میں آپ کی کیا مدد کر سکتا ہوں؟",
        },
    }

    def process_message(
        self,
        message: WhatsAppMessage,
    ) -> WhatsAppReply:

        language = self._normalize_language(
            message.language
        )

        if language == "auto":
            language = self._detect_language(
                message.message
            )

        intent = self._detect_intent(
            message.message
        )

        reply = self.REPLIES[language][intent]

        return WhatsAppReply(
            message=reply,
            intent=intent,
        )

    def _normalize_language(
        self,
        language: str,
    ) -> str:

        language = (language or "auto").lower()

        if language == "auto":
            return "auto"

        if "-" in language:
            language = language.split("-")[0]

        if language not in self.SUPPORTED_LANGUAGES:
            return "en"

        return language

    def _detect_language(
        self,
        text: str,
    ) -> str:

        normalized = text.casefold()

        urdu_markers = [
            "آرڈر",
            "ڈیلیوری",
            "قیمت",
            "پروڈکٹ",
            "انوائس",
            "ادائیگی",
            "میں",
            "آپ",
            "میرے",
            "کب",
            "ہے",
        ]

        if any(
            marker.casefold() in normalized
            for marker in urdu_markers
        ):
            return "ur"

        if any(
            "\u0600" <= char <= "\u06ff"
            for char in text
        ):
            return "ar"

        french_markers = [
            "commande",
            "livraison",
            "facture",
            "paiement",
            "produit",
            "prix",
            "bonjour",
            "merci",
            "je ",
            "vous ",
        ]

        if any(
            marker in normalized
            for marker in french_markers
        ):
            return "fr"

        return "en"

    def _detect_intent(
        self,
        text: str,
    ) -> str:

        normalized = text.casefold()

        for intent, languages in self.KEYWORDS.items():
            for keywords in languages.values():
                if any(
                    keyword.casefold() in normalized
                    for keyword in keywords
                ):
                    return intent

        return "general_support"