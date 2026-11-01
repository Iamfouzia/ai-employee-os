from app.communication.email.models import EmailDraftRequest
from app.communication.email.workflow import EmailWorkflowService


workflow = EmailWorkflowService()

profile = (
    workflow.gmail.service.users()
    .getProfile(userId="me")
    .execute()
)

my_email = profile["emailAddress"]

request = EmailDraftRequest(
    recipients=[my_email],
    subject="Project Meeting Follow-up",
    context=(
        "Thank the customer for attending today's meeting. "
        "Tell them that we will send the project proposal "
        "within two business days."
    ),
    tone="professional",
)

result = workflow.create_gmail_draft(request)

print("Email Assistant workflow successful")
print("Status:", result["status"])
print("Draft ID:", result["draft_id"])
print("Recipient:", result["recipient"])
print("Subject:", result["subject"])
print()
print("Generated body:")
print(result["body"])