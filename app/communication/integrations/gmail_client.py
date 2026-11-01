import base64
from email.message import EmailMessage as MIMEEmailMessage

from app.communication.email.models import EmailMessage
from app.communication.integrations.gmail_auth import get_gmail_service


class GmailClient:
    def __init__(self):
        self.service = get_gmail_service()

    def create_draft(
        self,
        recipient: str,
        subject: str,
        body: str,
    ) -> dict:
        message = MIMEEmailMessage()

        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        encoded_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode("utf-8")

        draft = (
            self.service.users()
            .drafts()
            .create(
                userId="me",
                body={
                    "message": {
                        "raw": encoded_message,
                    }
                },
            )
            .execute()
        )

        return draft

    def get_latest_inbox_messages(
        self,
        limit: int = 5,
    ) -> list[dict]:
        response = (
            self.service.users()
            .messages()
            .list(
                userId="me",
                labelIds=["INBOX"],
                maxResults=limit,
            )
            .execute()
        )

        messages = response.get("messages", [])
        results = []

        for message in messages:
            details = (
                self.service.users()
                .messages()
                .get(
                    userId="me",
                    id=message["id"],
                    format="metadata",
                    metadataHeaders=[
                        "From",
                        "To",
                        "Subject",
                        "Date",
                    ],
                )
                .execute()
            )

            headers = (
                details
                .get("payload", {})
                .get("headers", [])
            )

            header_map = {
                header["name"].lower(): header["value"]
                for header in headers
            }

            results.append(
                {
                    "id": details.get("id"),
                    "thread_id": details.get("threadId"),
                    "from": header_map.get("from", ""),
                    "to": header_map.get("to", ""),
                    "subject": header_map.get(
                        "subject",
                        "",
                    ),
                    "date": header_map.get("date", ""),
                }
            )

        return results

    def get_email(
        self,
        message_id: str,
    ) -> EmailMessage:
        details = (
            self.service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="full",
            )
            .execute()
        )

        payload = details.get("payload", {})
        headers = payload.get("headers", [])

        header_map = {
            header["name"].lower(): header["value"]
            for header in headers
        }

        body = self._extract_text_body(payload)

        recipients = []

        if header_map.get("to"):
            recipients = [
                item.strip()
                for item in header_map["to"].split(",")
            ]

        return EmailMessage(
            message_id=details.get("id"),
            thread_id=details.get("threadId"),
            sender=header_map.get("from", ""),
            recipients=recipients,
            subject=header_map.get("subject", ""),
            body=body,
        )

    def _extract_text_body(
        self,
        payload: dict,
    ) -> str:
        mime_type = payload.get("mimeType", "")
        body_data = (
            payload
            .get("body", {})
            .get("data")
        )

        if mime_type == "text/plain" and body_data:
            return self._decode_body(body_data)

        for part in payload.get("parts", []):
            result = self._extract_text_body(part)

            if result:
                return result

        return ""

    def _decode_body(
        self,
        data: str,
    ) -> str:
        padded_data = data + "=" * (-len(data) % 4)

        decoded = base64.urlsafe_b64decode(
            padded_data
        )

        return decoded.decode(
            "utf-8",
            errors="replace",
        )