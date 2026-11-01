from app.communication.email.models import EmailMessage
from app.communication.email.service import EmailAssistantService


service = EmailAssistantService()

urgent_email = EmailMessage(
    sender="customer@example.com",
    recipients=["support@company.com"],
    subject="Urgent payment issue",
    body=(
        "Our payment is not working. "
        "Can you please help us immediately?"
    ),
)

normal_email = EmailMessage(
    sender="customer@example.com",
    recipients=["sales@company.com"],
    subject="Pricing question",
    body="Could you please send me the pricing details?",
)

no_reply_email = EmailMessage(
    sender="newsletter@example.com",
    recipients=["user@company.com"],
    subject="Monthly Newsletter",
    body="Here is our monthly company newsletter.",
)


for name, email in [
    ("URGENT", urgent_email),
    ("NORMAL", normal_email),
    ("NO REPLY", no_reply_email),
]:
    analysis = service.analyze_email(email)

    print(f"--- {name} ---")
    print("Priority:", analysis.priority.value)
    print("Requires reply:", analysis.requires_reply)
    print(
        "Suggested follow-up:",
        analysis.suggested_follow_up_at,
    )
    print()