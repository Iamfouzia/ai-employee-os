from app.communication.email.service import EmailAssistantService
from app.communication.integrations.gmail_client import GmailClient


gmail = GmailClient()
assistant = EmailAssistantService()

messages = gmail.get_latest_inbox_messages(limit=1)

if not messages:
    print("Inbox is empty.")
else:
    email = gmail.get_email(messages[0]["id"])
    analysis = assistant.analyze_email(email)

    print("Gmail -> Email Assistant integration successful")
    print("Category:", analysis.category.value)
    print("Priority:", analysis.priority.value)
    print("Requires reply:", analysis.requires_reply)
    print("Summary:", analysis.summary[:100])