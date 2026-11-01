from app.communication.email.workflow import EmailWorkflowService


workflow = EmailWorkflowService()

result = workflow.create_reply_draft_for_latest_email(
    tone="professional"
)

print("Smart Gmail reply workflow successful")
print("Status:", result["status"])
print("Draft ID:", result["draft_id"])
print("Category:", result["category"])
print("Priority:", result["priority"])
print("Requires reply:", result["requires_reply"])
print("Reply subject:", result["reply_subject"])