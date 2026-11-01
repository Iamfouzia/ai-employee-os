from app.agents.base_agent import BaseAIEmployee
from app.nlu.schemas import TaskStep


class RecruiterAgent(BaseAIEmployee):
    name = "recruiter_agent"
    role = (
        "You are the AI Recruiter. You post job openings, schedule interviews, "
        "and send offer letters to candidates."
    )

    def register_tools(self) -> None:
        self.tools = {
            "post_job": self.post_job,
            "schedule_interview": self.schedule_interview,
            "send_offer_letter": self.send_offer_letter,
        }

    def post_job(self, step: TaskStep) -> str:
        return "Job posting created and published to job boards. [MOCK]"

    def schedule_interview(self, step: TaskStep) -> str:
        return f"Interview scheduled with {step.customer_name} on {step.date} at {step.time}. [MOCK]"

    def send_offer_letter(self, step: TaskStep) -> str:
        return f"Offer letter sent to {step.customer_name}. [MOCK]"