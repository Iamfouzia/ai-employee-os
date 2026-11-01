import requests

from app.communication.integrations.outlook_auth import (
    get_outlook_access_token,
)


token = get_outlook_access_token()

response = requests.get(
    "https://graph.microsoft.com/v1.0/me/messages",
    headers={
        "Authorization": f"Bearer {token}",
    },
    params={
        "$top": 1,
        "$select": "id,subject,from,receivedDateTime",
    },
    timeout=30,
)

print("Status:", response.status_code)

if response.ok:
    messages = response.json().get("value", [])

    print("Outlook connection successful")
    print("Messages returned:", len(messages))

    if messages:
        print("Latest subject:", messages[0].get("subject"))
else:
    print(response.text)