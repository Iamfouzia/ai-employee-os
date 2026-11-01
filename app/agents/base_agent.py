"""
Phase 4: Base AI Employee
------------------------------
Every specialized AI Employee (Sales, HR, Finance, Support...) extends this
class. It defines the shared contract:

- a `role` (system prompt describing this employee's persona/responsibilities)
- a `tools` registry (mock for now - action -> callable)
- an `execute()` method that takes a TaskStep and runs the matching tool

This is the template Phase 6 will copy 11 more times for the other employees.
"""

from typing import Callable
from app.nlu.schemas import TaskStep
from app.memory.long_term import log_customer_interaction


class BaseAIEmployee:
    role: str = "You are a generic AI employee."
    name: str = "base_employee"

    def __init__(self):
        self.tools: dict[str, Callable[[TaskStep], str]] = {}
        self.register_tools()

    def register_tools(self) -> None:
        """Subclasses override this to fill self.tools with {action_name: method}."""
        raise NotImplementedError

    def execute(self, step: TaskStep) -> str:
        """Run the tool matching this step's action. Falls back to a generic response."""
        tool = self.tools.get(step.action)
        if tool is None:
            result = f"[{self.name}] No tool registered for action '{step.action}' - skipped."
        else:
            result = tool(step)

        if step.customer_name:
            log_customer_interaction(step.customer_name, f"{self.name}: {result}")

        return result