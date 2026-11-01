"""
Run this to test Phase 7:
    python tests/test_phase7.py

Requires Redis running (Phase 3 setup) for the full graph test.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.knowledge.ingest import ingest_document
from app.knowledge.rag import answer_question
from app.agents.executive_assistant import build_graph

SAMPLE_DOCS = {
    "hr_policy": """
        Leave Policy: Employees are entitled to 14 days of paid annual leave
        per year. Leave requests must be submitted at least 3 days in advance
        through the HR portal. Sick leave requires a medical certificate for
        absences longer than 2 days.
    """,
    "refund_policy": """
        Refund Policy: Refunds are processed within 7 business days of a
        valid request. Customers must provide the original invoice number.
        Refunds are issued to the original payment method only. Products
        must be returned in original condition within 30 days of purchase.
    """,
}


def test_ingestion():
    print("--- Ingesting sample company documents ---")
    for name, text in SAMPLE_DOCS.items():
        n = ingest_document(name, text)
        print(f"  {name}: {n} chunk(s) stored")


def test_rag_standalone():
    print("\n--- RAG standalone ---")
    questions = [
        "How many days of annual leave do employees get?",
        "What is the refund policy?",
        "What is our company's stock price?",  # should trigger "don't know"
    ]
    for q in questions:
        result = answer_question(q)
        print(f"\nQ: {q}")
        print(f"A: {result['answer']}")


def test_full_graph():
    print("\n--- Full graph run (question should route to KnowledgeAgent) ---")
    app = build_graph()
    cmd = "What is the refund policy?"
    final_state = app.invoke({"session_id": "test-phase7-session", "raw_input": cmd})
    print(f"\nInput: {cmd}")
    for r in final_state["results"]:
        print(" ", r["outcome"])


if __name__ == "__main__":
    test_ingestion()
    test_rag_standalone()
    test_full_graph()