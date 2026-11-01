"""
Phase 4: AI Sales Manager
------------------------------
First concrete AI Employee. Tools are MOCKED (print + return a string) -
once the Quotation/Email/CRM modules exist elsewhere in the project,
swap the mock bodies for real API calls. The interface (action name ->
function taking a TaskStep) stays the same either way.
"""

from app.agents.base_agent import BaseAIEmployee
from app.nlu.schemas import TaskStep


class SalesAgent(BaseAIEmployee):
    name = "sales_agent"
    role = (
        "You are the AI Sales Manager. You handle quotations, sales meetings, "
        "and following up with customers on behalf of the business."
    )

    def register_tools(self) -> None:
        self.tools = {
            "send_quotation": self.send_quotation,
            "schedule_meeting": self.schedule_meeting,
            "send_reminder": self.send_reminder,
            "follow_up": self.follow_up,
        }

    # --- mock tools: replace bodies with real integrations later ---

    def send_quotation(self, step: TaskStep) -> str:
        # real version: generate PDF, attach branding/tax/discounts, email it
        return (f"Quotation created for {step.customer_name} "
                f"({step.quantity} units) and sent by email. [MOCK]")

    def schedule_meeting(self, step: TaskStep) -> str:
        # real version: Google Calendar / Outlook API call
        return (f"Meeting scheduled with {step.customer_name} "
                f"on {step.date} at {step.time}. [MOCK]")

    def send_reminder(self, step: TaskStep) -> str:
        # real version: this only actually fires later, once the condition
        # (e.g. "no reply in 3 days") is checked by a scheduler - Phase 4
        # just registers the intent to remind.
        return (f"Reminder scheduled for {step.customer_name} - "
                f"condition: '{step.condition}'. [MOCK]")

    def follow_up(self, step: TaskStep) -> str:
        return f"Follow-up message sent to {step.customer_name}. [MOCK]"


if __name__ == "__main__":
    agent = SalesAgent()
    sample_step = TaskStep(
        step_id=1, category="sales", action="send_quotation",
        customer_name="John", quantity=25,
    )
    print(agent.execute(sample_step))