"""
Run this to test Phase 4:
    python tests/test_phase4.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.agents.employees.sales_agent import SalesAgent
from app.nlu.schemas import TaskStep
from app.agents.executive_assistant import build_graph


def test_sales_agent_standalone():
    print("\n--- SalesAgent standalone ---")
    agent = SalesAgent()
    steps = [
        TaskStep(step_id=1, category="sales", action="send_quotation", customer_name="John", quantity=25),
        TaskStep(step_id=2, category="sales", action="schedule_meeting", customer_name="John", date="Friday", time="3 PM"),
        TaskStep(step_id=3, category="sales", action="unknown_action", customer_name="John"),  # tests fallback
    ]
    for s in steps:
        print(agent.execute(s))


def test_full_graph():
    print("\n--- Full graph run (Sales category should route to real SalesAgent) ---")
    app = build_graph()
    cmd = "Send a quotation to John for 25 laptops and schedule a meeting Friday at 3 PM"
    final_state = app.invoke({"session_id": "test-phase4-session", "raw_input": cmd})
    for r in final_state["results"]:
        print(r["outcome"])


if __name__ == "__main__":
    test_sales_agent_standalone()
    test_full_graph()