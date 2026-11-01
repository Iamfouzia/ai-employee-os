from app.communication.email.models import EmailDraftRequest
from app.communication.email.outlook_workflow import (
    OutlookEmailWorkflowService,
)


workflow = OutlookEmailWorkflowService()

request = EmailDraftRequest(
    recipients=["hafizmelad71@gmail.com"],
    subject="AI Employee OS Outlook Workflow Test",
    context=(
        "Thank the customer for contacting us and tell them "
        "we will reply with pricing information shortly."
    ),
    tone="professional",
)

result = workflow.create_draft(request)

print("Outlook Email Assistant workflow successful")
print("Status:", result["status"])
print("Subject:", result["subject"])
print("Is draft:", result["is_draft"])