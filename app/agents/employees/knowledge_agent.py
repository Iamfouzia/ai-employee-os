from app.agents.base_agent import BaseAIEmployee
from app.nlu.schemas import TaskStep
from app.knowledge.rag import answer_question


class KnowledgeAgent(BaseAIEmployee):
    name = "knowledge_agent"
    role = (
        "You answer employee/customer questions using the company's internal "
        "knowledge base (policies, product info, FAQs) via retrieval-augmented generation."
    )

    def register_tools(self) -> None:
        self.tools = {
            "answer_question": self.answer_question_tool,
        }

    def answer_question_tool(self, step: TaskStep) -> str:
        question = step.question_text or step.action.replace("_", " ")
        result = answer_question(question)
        return result["answer"]