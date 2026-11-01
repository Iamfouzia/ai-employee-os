from datetime import datetime, timezone

from app.communication.email.models import EmailMessage
from app.communication.email.service import EmailAssistantService
from app.communication.integrations.calendar_client import GoogleCalendarClient


email = EmailMessage(
    sender="customer@example.com",
    recipients=["support@company.com"],
    subject="Urgent payment issue",
    body="Can you please help us immediately?",
)

assistant = EmailAssistantService()
calendar = GoogleCalendarClient()

analysis = assistant.analyze_email(email)

print("Requires reply:", analysis.requires_reply)
print("Follow-up at:", analysis.suggested_follow_up_at)

if analysis.suggested_follow_up_at:
    event = calendar.create_follow_up_event(
        title="Follow up: Urgent payment issue",
        start_at=analysis.suggested_follow_up_at,
        description="Controlled follow-up workflow test.",
    )

    print("Follow-up event created successfully")
    print("Event ID:", event.get("id"))
else:
    print("No follow-up created")