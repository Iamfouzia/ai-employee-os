from app.communication.email.ai_service import EmailAIService
from app.communication.email.models import EmailDraftRequest
from app.communication.integrations.outlook_client import OutlookClient


class OutlookEmailWorkflowService:
    def __init__(self):
        self.ai = EmailAIService()
        self.outlook = OutlookClient()

    def create_draft(
        self,
        request: EmailDraftRequest,
    ) -> dict:

        generated = self.ai.generate_draft(request)

        draft = self.outlook.create_draft(
            recipient=request.recipients[0],
            subject=generated.subject,
            body=generated.body,
        )

        return {
            "status": "outlook_draft_created",
            "draft_id": draft["id"],
            "subject": draft["subject"],
            "is_draft": draft["isDraft"],
        }