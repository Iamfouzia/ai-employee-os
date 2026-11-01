from app.agents.base_agent import BaseAIEmployee
from app.nlu.schemas import TaskStep


class AccountantAgent(BaseAIEmployee):
    name = "accountant_agent"
    role = (
        "You are the AI Accountant. You reconcile accounts, generate financial "
        "reports, and handle tax filing preparation."
    )

    def register_tools(self) -> None:
        self.tools = {
            "reconcile_accounts": self.reconcile_accounts,
            "generate_report": self.generate_report,
            "file_tax": self.file_tax,
        }

    def reconcile_accounts(self, step: TaskStep) -> str:
        return "Accounts reconciled against bank records. [MOCK]"

    def generate_report(self, step: TaskStep) -> str:
        return "Financial report generated (revenue, expenses, forecast). [MOCK]"

    def file_tax(self, step: TaskStep) -> str:
        return "Tax filing documents prepared. [MOCK]"