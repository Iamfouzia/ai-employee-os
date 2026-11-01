"""
Phase 2: Executive Assistant Orchestrator (LangGraph)
--------------------------------------------------------
Graph shape:

    Input -> Planner Node -> Execute Step Node --(loop)--> Execute Step Node -> Final Response

Execution is MOCKED for now (just prints/logs what it would do). Real API
calls (Gmail, CRM, Calendar...) get wired in once those modules exist -
this graph's job right now is only to prove the planning + sequencing logic works.
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END

from app.agents.planner import build_task_plan
from app.nlu.schemas import TaskPlan, TaskStep, IntentCategory
from app.memory.short_term import save_session_state, append_conversation_turn
from app.agents.employees.ceo_agent import CEOAgent
from app.agents.employees.sales_agent import SalesAgent
from app.agents.employees.support_agent import SupportAgent
from app.agents.employees.hr_agent import HRAgent
from app.agents.employees.recruiter_agent import RecruiterAgent
from app.agents.employees.finance_agent import FinanceAgent
from app.agents.employees.accountant_agent import AccountantAgent
from app.agents.employees.marketing_agent import MarketingAgent
from app.agents.employees.content_agent import ContentAgent
from app.agents.employees.legal_agent import LegalAgent
from app.agents.employees.inventory_agent import InventoryAgent
from app.agents.employees.procurement_agent import ProcurementAgent
from app.agents.employees.knowledge_agent import KnowledgeAgent

# Registry: category -> AI Employee instance. All 12 employees from the PDF are now wired.
EMPLOYEE_REGISTRY = {
    IntentCategory.CEO: CEOAgent(),
    IntentCategory.SALES: SalesAgent(),
    IntentCategory.SUPPORT: SupportAgent(),
    IntentCategory.HR: HRAgent(),
    IntentCategory.RECRUITMENT: RecruiterAgent(),
    IntentCategory.FINANCE: FinanceAgent(),
    IntentCategory.ACCOUNTING: AccountantAgent(),
    IntentCategory.MARKETING: MarketingAgent(),
    IntentCategory.CONTENT: ContentAgent(),
    IntentCategory.LEGAL: LegalAgent(),
    IntentCategory.INVENTORY: InventoryAgent(),
    IntentCategory.PROCUREMENT: ProcurementAgent(),
    IntentCategory.GENERAL: KnowledgeAgent(),
}


class AssistantState(TypedDict):
    session_id: str
    raw_input: str
    task_plan: TaskPlan
    current_step_index: int
    results: list[dict]


def planner_node(state: AssistantState) -> AssistantState:
    """Break the raw command into an ordered TaskPlan."""
    append_conversation_turn(state["session_id"], "user", state["raw_input"])
    plan = build_task_plan(state["raw_input"])
    return {**state, "task_plan": plan, "current_step_index": 0, "results": []}


def execute_step_node(state: AssistantState) -> AssistantState:
    """Route the current step to its AI Employee (or mock it if none registered yet)."""
    plan = state["task_plan"]
    idx = state["current_step_index"]
    step: TaskStep = plan.steps[idx]

    if step.depends_on is not None:
        outcome = f"[SCHEDULED/CONDITIONAL] step {step.step_id} ({step.action}) " \
                  f"waits on step {step.depends_on}, condition: '{step.condition}'"
    else:
        employee = EMPLOYEE_REGISTRY.get(step.category)
        if employee is not None:
            outcome = f"[step {step.step_id}] {employee.execute(step)}"
        else:
            # no AI Employee built for this category yet (Phase 6 will fill these in)
            outcome = f"[MOCK - no employee registered] step {step.step_id}: {step.action} " \
                      f"-> category={step.category.value}, customer={step.customer_name}"
    # -----------------------------------------------------------------------------

    new_results = state["results"] + [{"step_id": step.step_id, "outcome": outcome}]
    new_state = {**state, "results": new_results, "current_step_index": idx + 1}

    save_session_state(state["session_id"], new_state)
    return new_state


def should_continue(state: AssistantState) -> str:
    """Conditional edge: loop back to execute_step until all steps are done
    (also used right after planning, to handle an empty plan safely)."""
    if state["current_step_index"] < len(state["task_plan"].steps):
        return "continue"
    return "done"


def build_graph():
    graph = StateGraph(AssistantState)
    graph.add_node("planner", planner_node)
    graph.add_node("execute_step", execute_step_node)

    graph.set_entry_point("planner")
    # conditional (not unconditional) - an empty plan (e.g. every step got
    # filtered as a hallucination) must skip straight to END, not crash
    # execute_step_node trying to access plan.steps[0].
    graph.add_conditional_edges(
        "planner",
        should_continue,
        {"continue": "execute_step", "done": END},
    )
    graph.add_conditional_edges(
        "execute_step",
        should_continue,
        {"continue": "execute_step", "done": END},
    )
    return graph.compile()


if __name__ == "__main__":
    app = build_graph()
    sample = ("Send a quotation to John for 25 laptops, schedule a meeting "
              "Friday at 3 PM, and remind me if he doesn't reply within three days")
    final_state = app.invoke({"session_id": "demo-session", "raw_input": sample})

    print(f"\nInput: {sample}\n")
    for r in final_state["results"]:
        print(r["outcome"])