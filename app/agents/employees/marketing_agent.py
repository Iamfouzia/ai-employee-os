from app.agents.base_agent import BaseAIEmployee
from app.nlu.schemas import TaskStep


class MarketingAgent(BaseAIEmployee):
    name = "marketing_agent"
    role = (
        "You are the AI Marketing Assistant. You launch campaigns, post social "
        "media updates, and analyze campaign performance."
    )

    def register_tools(self) -> None:
        self.tools = {
            "launch_campaign": self.launch_campaign,
            "post_social_update": self.post_social_update,
            "analyze_campaign": self.analyze_campaign,
        }

    def launch_campaign(self, step: TaskStep) -> str:
        return "Marketing campaign launched across configured channels. [MOCK]"

    def post_social_update(self, step: TaskStep) -> str:
        return "Social media update posted. [MOCK]"

    def analyze_campaign(self, step: TaskStep) -> str:
        return "Campaign performance analyzed - engagement and reach report ready. [MOCK]"