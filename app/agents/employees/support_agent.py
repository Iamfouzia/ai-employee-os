from app.agents.base_agent import BaseAIEmployee
from app.nlu.schemas import TaskStep


class SupportAgent(BaseAIEmployee):
    name = "support_agent"
    role = (
        "You are the AI Customer Support Agent. You respond to tickets, "
        "resolve complaints, and escalate unresolved issues."
    )

    def register_tools(self) -> None:
        self.tools = {
            "respond_to_ticket": self.respond_to_ticket,
            "resolve_complaint": self.resolve_complaint,
            "escalate_ticket": self.escalate_ticket,
        }

    def respond_to_ticket(self, step: TaskStep) -> str:
        return f"Support ticket for {step.customer_name} answered. [MOCK]"

    def resolve_complaint(self, step: TaskStep) -> str:
        return f"Complaint from {step.customer_name} resolved and logged. [MOCK]"

    def escalate_ticket(self, step: TaskStep) -> str:
        return f"Ticket for {step.customer_name} escalated to a human agent. [MOCK]"