from app.communication.integrations.gmail_client import GmailClient


gmail = GmailClient()

profile = (
    gmail.service.users()
    .getProfile(userId="me")
    .execute()
)

my_email = profile["emailAddress"]

draft = gmail.create_draft(
    recipient=my_email,
    subject="AI Employee OS - Draft Test",
    body=(
        "Hello,\n\n"
        "This draft was created automatically by the "
        "AI Employee OS Communication Module.\n\n"
        "Best regards,\n"
        "AI Employee OS"
    ),
)

print("Gmail draft created successfully")
print("Draft ID:", draft.get("id"))