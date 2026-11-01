from app.agents.base_agent import BaseAIEmployee
from app.nlu.schemas import TaskStep


class HRAgent(BaseAIEmployee):
    name = "hr_agent"
    role = (
        "You are the AI HR Assistant. You handle employee onboarding, "
        "company policy updates, and leave requests."
    )

    def register_tools(self) -> None:
        self.tools = {
            "onboard_employee": self.onboard_employee,
            "update_policy": self.update_policy,
            "manage_leave_request": self.manage_leave_request,
        }

    def onboard_employee(self, step: TaskStep) -> str:
        return f"Onboarding started for {step.customer_name}, starting {step.date or 'TBD'}. [MOCK]"

    def update_policy(self, step: TaskStep) -> str:
        return "Company policy document updated and shared with staff. [MOCK]"

    def manage_leave_request(self, step: TaskStep) -> str:
        return f"Leave request for {step.customer_name} processed for {step.date or 'requested date'}. [MOCK]"