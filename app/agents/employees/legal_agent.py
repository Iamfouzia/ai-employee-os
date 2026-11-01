from app.agents.base_agent import BaseAIEmployee
from app.nlu.schemas import TaskStep


class LegalAgent(BaseAIEmployee):
    name = "legal_agent"
    role = (
        "You are the AI Legal Assistant. You review contracts, draft "
        "agreements, and check regulatory compliance."
    )

    def register_tools(self) -> None:
        self.tools = {
            "review_contract": self.review_contract,
            "draft_agreement": self.draft_agreement,
            "check_compliance": self.check_compliance,
        }

    def review_contract(self, step: TaskStep) -> str:
        return f"Contract for {step.customer_name or 'the deal'} reviewed - flagged clauses noted. [MOCK]"

    def draft_agreement(self, step: TaskStep) -> str:
        return "Agreement draft prepared. [MOCK]"

    def check_compliance(self, step: TaskStep) -> str:
        return "Compliance check completed against current regulations. [MOCK]"