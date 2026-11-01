from app.agents.base_agent import BaseAIEmployee
from app.nlu.schemas import TaskStep


class ContentAgent(BaseAIEmployee):
    name = "content_agent"
    role = (
        "You are the AI Content Writer. You write blog posts, product "
        "descriptions, and ad copy for the business."
    )

    def register_tools(self) -> None:
        self.tools = {
            "write_blog_post": self.write_blog_post,
            "write_product_description": self.write_product_description,
            "write_ad_copy": self.write_ad_copy,
        }

    def write_blog_post(self, step: TaskStep) -> str:
        return "Blog post drafted and ready for review. [MOCK]"

    def write_product_description(self, step: TaskStep) -> str:
        return "Product description written. [MOCK]"

    def write_ad_copy(self, step: TaskStep) -> str:
        return "Ad copy variants generated. [MOCK]"