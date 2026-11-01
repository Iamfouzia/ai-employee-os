from app.communication.email.workflow import EmailWorkflowService

workflow = EmailWorkflowService()

result = workflow.create_reply_draft_for_latest_email()

print("Workflow successful")
print(result)