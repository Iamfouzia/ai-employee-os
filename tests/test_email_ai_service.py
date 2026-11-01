from app.communication.email.ai_service import EmailAIService
from app.communication.email.models import EmailDraftRequest


service = EmailAIService()

request = EmailDraftRequest(
    recipients=["customer@example.com"],
    subject="Pricing Information",
    context=(
        "Thank the customer for contacting us. "
        "Tell them that our sales team will send the full "
        "pricing details within one business day."
    ),
    tone="professional",
)

draft = service.generate_draft(request)

print("Subject:", draft.subject)
print()
print("Body:")
print(draft.body)