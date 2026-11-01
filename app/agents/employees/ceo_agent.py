from app.agents.base_agent import BaseAIEmployee
from app.nlu.schemas import TaskStep


class CEOAgent(BaseAIEmployee):
    name = "ceo_agent"
    role = (
        "You are the AI CEO Assistant. You handle high-level approvals, "
        "review reports, and escalate critical issues to the business owner."
    )

    def register_tools(self) -> None:
        self.tools = {
            "approve_request": self.approve_request,
            "review_report": self.review_report,
            "escalate_issue": self.escalate_issue,
        }

    def approve_request(self, step: TaskStep) -> str:
        return f"Request reviewed and approved (or flagged for manual review). [MOCK]"

    def review_report(self, step: TaskStep) -> str:
        return "Report reviewed - summary and key insights prepared. [MOCK]"

    def escalate_issue(self, step: TaskStep) -> str:
        return f"Issue escalated to the business owner for {step.customer_name or 'the relevant matter'}. [MOCK]"