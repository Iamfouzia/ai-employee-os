from app.agents.base_agent import BaseAIEmployee
from app.nlu.schemas import TaskStep


class InventoryAgent(BaseAIEmployee):
    name = "inventory_agent"
    role = (
        "You are the AI Inventory Manager. You update stock levels, check "
        "inventory availability, and trigger reorders."
    )

    def register_tools(self) -> None:
        self.tools = {
            "update_stock": self.update_stock,
            "check_inventory": self.check_inventory,
            "reorder_stock": self.reorder_stock,
        }

    def update_stock(self, step: TaskStep) -> str:
        return f"Stock levels updated ({step.quantity or 'N/A'} units). [MOCK]"

    def check_inventory(self, step: TaskStep) -> str:
        return "Inventory availability checked. [MOCK]"

    def reorder_stock(self, step: TaskStep) -> str:
        return f"Reorder triggered for {step.quantity or 'N/A'} units. [MOCK]"