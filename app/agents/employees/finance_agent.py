from app.agents.base_agent import BaseAIEmployee
from app.nlu.schemas import TaskStep


class FinanceAgent(BaseAIEmployee):
    name = "finance_agent"
    role = (
        "You are the AI Finance Assistant. You generate invoices, process payments, "
        "and track business expenses."
    )

    def register_tools(self) -> None:
        self.tools = {
            "generate_invoice": self.generate_invoice,
            "process_payment": self.process_payment,
            "track_expense": self.track_expense,
        }

    def generate_invoice(self, step: TaskStep) -> str:
        return f"Invoice generated for {step.customer_name} ({step.quantity or 'N/A'} units). [MOCK]"

    def process_payment(self, step: TaskStep) -> str:
        return f"Payment processed for {step.customer_name}. [MOCK]"

    def track_expense(self, step: TaskStep) -> str:
        return "Expense logged and categorized. [MOCK]"