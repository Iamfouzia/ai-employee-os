import requests

from app.communication.integrations.outlook_auth import (
    get_outlook_access_token,
)


GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


class OutlookClient:
    def _headers(self) -> dict:
        token = get_outlook_access_token()

        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def get_latest_inbox_messages(
        self,
        limit: int = 5,
    ) -> list[dict]:

        response = requests.get(
            f"{GRAPH_BASE_URL}/me/mailFolders/inbox/messages",
            headers=self._headers(),
            params={
                "$top": limit,
                "$select": (
                    "id,subject,from,toRecipients,"
                    "receivedDateTime,bodyPreview"
                ),
                "$orderby": "receivedDateTime desc",
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.json().get("value", [])

    def create_draft(
        self,
        recipient: str,
        subject: str,
        body: str,
    ) -> dict:

        payload = {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body,
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": recipient,
                    }
                }
            ],
        }

        response = requests.post(
            f"{GRAPH_BASE_URL}/me/messages",
            headers=self._headers(),
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()