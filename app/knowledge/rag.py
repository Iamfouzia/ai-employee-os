"""
Phase 7b: RAG Query Engine
------------------------------
Two-step RAG:
1. Retrieve the most relevant chunks from company_knowledge (ChromaDB, semantic search)
2. Feed those chunks + the question to the local LLM, instructed to answer
   ONLY from the provided context (reduces hallucination on company-specific facts)

Reuses the same local model already loaded in app/nlu/intent_classifier.py -
no second model download needed.
"""

from app.memory.long_term import query_knowledge_base
from app.core.llm_router import route_and_generate

RAG_SYSTEM_PROMPT = """You are a helpful company assistant. Answer the user's
question using ONLY the context provided below. If the context does not
contain the answer, say "I don't have that information in the company
knowledge base" - do not make up an answer.

Context:
{context}"""


def answer_question(question: str, n_context_chunks: int = 3) -> dict:
    """Retrieve relevant chunks and generate a grounded answer via the LLM router
    (simple questions -> local model, complex/long ones -> hosted model if available).
    Returns {"answer": str, "sources": list[str], "provider": str}."""
    chunks = query_knowledge_base(question, n_results=n_context_chunks)

    if not chunks:
        return {
            "answer": "I don't have that information in the company knowledge base.",
            "sources": [],
            "provider": None,
        }

    context = "\n\n".join(chunks)
    system_prompt = RAG_SYSTEM_PROMPT.format(context=context)
    result = route_and_generate(system_prompt, question, text_for_complexity=question)

    return {"answer": result["text"], "sources": chunks, "provider": result["provider"]}


if __name__ == "__main__":
    questions = [
        "What is the refund policy?",
        "How many days of annual leave do employees get?",
        "What is our company's stock price?",  # should trigger the "don't know" fallback
    ]
    for q in questions:
        print(f"\nQ: {q}")
        result = answer_question(q)
        print(f"A: {result['answer']}")