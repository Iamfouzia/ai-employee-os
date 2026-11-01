"""
Run this to test Phase 3:
    python tests/test_phase3.py

Requires Redis running locally. Quickest way if you don't have it installed:
    docker run -d -p 6379:6379 redis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.memory.short_term import (
    append_conversation_turn, get_conversation_history,
    save_session_state, load_session_state,
)
from app.memory.long_term import log_customer_interaction, get_customer_history
from app.agents.executive_assistant import build_graph


def test_short_term():
    print("\n--- Short-term memory (Redis) ---")
    sid = "test-phase3-session"
    append_conversation_turn(sid, "user", "Send a quotation to John for 25 laptops")
    append_conversation_turn(sid, "assistant", "Done, tracking his reply.")
    save_session_state(sid, {"raw_input": "test", "current_step_index": 1})

    print("Conversation history:", get_conversation_history(sid))
    print("Saved state:", load_session_state(sid))


def test_long_term():
    print("\n--- Long-term memory (ChromaDB) ---")
    log_customer_interaction("John", "Sent quotation for 25 laptops.")
    log_customer_interaction("John", "Scheduled follow-up meeting for Friday.")
    print("John's history:", get_customer_history("John"))


def test_full_graph_with_memory():
    print("\n--- Full graph run (should log to both memories) ---")
    app = build_graph()
    cmd = "Send a quotation to John for 25 laptops"
    final_state = app.invoke({"session_id": "test-phase3-session", "raw_input": cmd})
    for r in final_state["results"]:
        print(r["outcome"])

    # run the SAME customer again - "prior history" count in the output should now be > 0
    print("\n--- Running again for the same customer (memory should show prior history) ---")
    final_state_2 = app.invoke({"session_id": "test-phase3-session-2", "raw_input": cmd})
    for r in final_state_2["results"]:
        print(r["outcome"])


if __name__ == "__main__":
    test_short_term()
    test_long_term()
    test_full_graph_with_memory()