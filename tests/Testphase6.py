"""
Run this to test Phase 6:
    python tests/test_phase6.py

Sends commands that should route to different AI Employees, to confirm
all 12 are correctly wired into the registry.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.agents.executive_assistant import build_graph, EMPLOYEE_REGISTRY

SAMPLE_COMMANDS = [
    "Send a quotation to John for 25 laptops",                              # sales
    "Onboard Sara as a new employee starting Monday",                      # hr
    "Post a job opening for a backend developer and schedule an interview with Ali", # recruitment
    "Generate an invoice for Zainab",                                       # finance
    "Reconcile this month's accounts and generate a report",                # accounting
    "Launch a social media campaign for the new product",                   # marketing
    "Write a blog post about our new laptop lineup",                        # content
    "Review the contract with our new vendor",                              # legal
    "Check inventory levels for laptops and reorder if low",                # inventory
    "Create a purchase order for 100 units from our supplier",              # procurement
    "Respond to the customer support ticket from Ahmed",                    # support
    "Review this month's performance report",                               # ceo
]

if __name__ == "__main__":
    print(f"Registered employees: {[c.value for c in EMPLOYEE_REGISTRY.keys()]}\n")

    app = build_graph()
    for i, cmd in enumerate(SAMPLE_COMMANDS):
        print(f"\nInput: {cmd}")
        final_state = app.invoke({"session_id": f"phase6-test-{i}", "raw_input": cmd})
        for r in final_state["results"]:
            print(" ", r["outcome"])