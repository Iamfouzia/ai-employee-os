from email.utils import parseaddr

from app.communication.email.ai_service import EmailAIService
from app.communication.email.models import EmailDraftRequest
from app.communication.email.service import EmailAssistantService
from app.communication.integrations.gmail_client import GmailClient
from app.communication.integrations.calendar_client import GoogleCalendarClient


class EmailWorkflowService:
    def __init__(self):
        self.email_ai = EmailAIService()
        self.email_analyzer = EmailAssistantService()
        self.gmail = GmailClient()
        self.calendar = GoogleCalendarClient()

    def create_gmail_draft(self, request: EmailDraftRequest) -> dict:
        draft = self.email_ai.generate_draft(request)

        result = self.gmail.create_draft(
            recipient=request.recipients[0],
            subject=draft.subject,
            body=draft.body,
        )

        return {
            "status": "draft_created",
            "draft_id": result.get("id"),
        }

    def create_reply_draft_for_latest_email(
        self,
        tone: str = "professional",
    ) -> dict:

        messages = self.gmail.get_latest_inbox_messages(limit=1)

        if not messages:
            raise ValueError("No inbox messages found.")

        email = self.gmail.get_email(messages[0]["id"])
        analysis = self.email_analyzer.analyze_email(email)

        reply = self.email_ai.generate_reply(
            email=email,
            tone=tone,
        )

        _, sender = parseaddr(email.sender)

        draft = self.gmail.create_draft(
            recipient=sender,
            subject=reply.subject,
            body=reply.body,
        )

        calendar_event = None

        if analysis.suggested_follow_up_at:
            calendar_event = self.calendar.create_follow_up_event(
                title=f"Follow up: {email.subject}",
                start_at=analysis.suggested_follow_up_at,
                description=(
                    f"Follow up regarding email from {sender}\n"
                    f"Priority: {analysis.priority.value}\n"
                    f"Category: {analysis.category.value}"
                ),
            )

        return {
            "status": "reply_draft_created",
            "draft_id": draft.get("id"),
            "category": analysis.category.value,
            "priority": analysis.priority.value,
            "follow_up_created": calendar_event is not None,
            "calendar_event_id": (
                calendar_event.get("id")
                if calendar_event
                else None
            ),
        }