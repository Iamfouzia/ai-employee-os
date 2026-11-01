"""
Run this to test Phase 2 (after Phase 1 is working):
    python tests/test_phase2.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.agents.executive_assistant import build_graph

SAMPLE_COMMANDS = [
    "Send a quotation to John for 25 laptops, schedule a meeting Friday at 3 PM, "
    "and remind me if he doesn't reply within three days",

    "Onboard Sara as a new HR hire starting Monday and schedule her orientation meeting",

    "Generate this month's revenue report and email it to the finance team",
]

if __name__ == "__main__":
    app = build_graph()
    for cmd in SAMPLE_COMMANDS:
        print(f"\n{'='*70}\nInput: {cmd}\n{'='*70}")
        final_state = app.invoke({"raw_input": cmd})
        for r in final_state["results"]:
            print(r["outcome"])