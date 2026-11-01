"""
Run this to test Phase 5:
    python tests/test_phase5.py

Works with ZERO API keys configured - everything falls back to the local
model automatically. Add keys to .env to see it actually route to a hosted
provider for complex tasks.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import available_providers
from app.core.llm_router import route_and_generate, classify_complexity
from app.nlu.schemas import IntentCategory
from app.knowledge.ingest import ingest_document
from app.knowledge.rag import answer_question


def test_availability():
    print("--- Available providers ---")
    print(available_providers())
    print("(only 'local' will show unless you've added API keys to .env)\n")


def test_complexity_classification():
    print("--- Complexity classification ---")
    cases = [
        ("Send a quotation to John", None, "simple"),
        ("What time is the meeting?", None, "simple"),
        ("Review this vendor contract for compliance risks", IntentCategory.LEGAL, "complex"),
        ("Reconcile accounts", IntentCategory.ACCOUNTING, "complex"),
    ]
    for text, category, expected in cases:
        result = classify_complexity(text, category)
        print(f"  '{text}' (category={category}) -> {result} (expected {expected})")


def test_routing():
    print("\n--- Routing (no keys set -> should all say 'local') ---")
    simple = route_and_generate(
        "You are a helpful assistant.", "Summarize: quotation sent to John.",
        text_for_complexity="Summarize: quotation sent to John.",
    )
    print(f"Simple task -> provider: {simple['provider']}")

    complex_case = route_and_generate(
        "You are a legal assistant.", "What should I check before signing a vendor contract?",
        text_for_complexity="What should I check before signing a vendor contract?",
        category=IntentCategory.LEGAL,
    )
    print(f"Complex/legal task -> provider: {complex_case['provider']} "
          f"(would be 'anthropic'/'openai'/'gemini' if a key were set)")


def test_rag_with_routing():
    print("\n--- RAG through the router ---")
    ingest_document("refund_policy", "Refunds are processed within 7 business days.")
    result = answer_question("What is the refund policy?")
    print(f"Answer: {result['answer']}")
    print(f"Handled by: {result['provider']}")


if __name__ == "__main__":
    test_availability()
    test_complexity_classification()
    test_routing()
    test_rag_with_routing()