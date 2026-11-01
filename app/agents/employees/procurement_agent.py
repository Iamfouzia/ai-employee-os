from app.agents.base_agent import BaseAIEmployee
from app.nlu.schemas import TaskStep


class ProcurementAgent(BaseAIEmployee):
    name = "procurement_agent"
    role = (
        "You are the AI Procurement Assistant. You create purchase orders, "
        "negotiate with vendors, and track deliveries."
    )

    def register_tools(self) -> None:
        self.tools = {
            "create_purchase_order": self.create_purchase_order,
            "negotiate_vendor": self.negotiate_vendor,
            "track_delivery": self.track_delivery,
        }

    def create_purchase_order(self, step: TaskStep) -> str:
        return f"Purchase order created for {step.quantity or 'N/A'} units. [MOCK]"

    def negotiate_vendor(self, step: TaskStep) -> str:
        return f"Vendor negotiation initiated with {step.customer_name or 'the supplier'}. [MOCK]"

    def track_delivery(self, step: TaskStep) -> str:
        return "Delivery status tracked and updated. [MOCK]"