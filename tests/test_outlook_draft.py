from app.communication.integrations.outlook_client import (
    OutlookClient,
)


client = OutlookClient()

draft = client.create_draft(
    recipient="hafizmelad71@gmail.com",
    subject="AI Employee OS Outlook Test",
    body=(
        "This is a test draft created by "
        "AI Employee OS Communication Module."
    ),
)

print("Outlook draft creation successful")
print("Draft ID:", draft["id"])
print("Subject:", draft["subject"])
print("Is draft:", draft["isDraft"])