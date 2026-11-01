from app.communication.integrations.gmail_auth import (
    get_gmail_service,
)


service = get_gmail_service()

profile = (
    service.users()
    .getProfile(userId="me")
    .execute()
)

print("Gmail connection successful")
print("Email:", profile.get("emailAddress"))
print("Messages:", profile.get("messagesTotal"))
print("Threads:", profile.get("threadsTotal"))