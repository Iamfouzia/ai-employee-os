from app.communication.email.models import EmailMessage
from app.communication.email.service import EmailAssistantService


service = EmailAssistantService()

email = EmailMessage(
    sender="customer@example.com",
    recipients=["sales@company.com"],
    subject="Urgent: Need pricing",
    body="Can you please send me your pricing today?",
)

result = service.analyze_email(email)

print("Summary:", result.summary)
print("Category:", result.category.value)
print("Priority:", result.priority.value)
print("Requires reply:", result.requires_reply)