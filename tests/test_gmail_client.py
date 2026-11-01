from app.communication.integrations.gmail_client import GmailClient


client = GmailClient()

messages = client.get_latest_inbox_messages(limit=5)

print(f"Found {len(messages)} messages")
print()

for index, message in enumerate(messages, start=1):
    print(f"--- Email {index} ---")
    print("From:", message["from"])
    print("To:", message["to"])
    print("Subject:", message["subject"])
    print("Date:", message["date"])
    print()