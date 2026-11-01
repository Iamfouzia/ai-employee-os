"""
Phase 3b: Long-Term Memory (ChromaDB)
------------------------------------------
Two separate collections:

1. "customer_history"  -> past interactions per customer (persists forever,
   used so the Executive Assistant remembers "we already sent John a
   quotation last week" across sessions, not just within one conversation).

2. "company_knowledge"  -> company docs/policies for RAG (Phase 7 will build
   on this, but the store itself is set up now so ingestion can start early).

Uses ChromaDB's default local embedding function - no extra API calls needed.
"""

import chromadb
from datetime import datetime, timezone

_client = chromadb.PersistentClient(path="./chroma_store")

customer_history = _client.get_or_create_collection("customer_history")
company_knowledge = _client.get_or_create_collection("company_knowledge")


def log_customer_interaction(customer_name: str, summary: str, metadata: dict | None = None) -> None:
    """Store one interaction with a customer (e.g. 'sent quotation for 25 laptops')."""
    doc_id = f"{customer_name}-{datetime.now(timezone.utc).isoformat()}"
    meta = {"customer_name": customer_name, "timestamp": datetime.now(timezone.utc).isoformat()}
    if metadata:
        meta.update(metadata)
    customer_history.add(documents=[summary], ids=[doc_id], metadatas=[meta])


def get_customer_history(customer_name: str, n_results: int = 5) -> list[str]:
    """Retrieve the most relevant past interactions for a given customer."""
    results = customer_history.query(
        query_texts=[customer_name],
        n_results=n_results,
        where={"customer_name": customer_name},
    )
    return results["documents"][0] if results["documents"] else []


def add_knowledge_document(doc_id: str, text: str, metadata: dict | None = None) -> None:
    """Ingest a company doc/policy chunk into the knowledge base (used later for RAG)."""
    company_knowledge.add(documents=[text], ids=[doc_id], metadatas=[metadata or {}])


def query_knowledge_base(question: str, n_results: int = 3) -> list[str]:
    """Semantic search over company knowledge - returns the most relevant chunks."""
    results = company_knowledge.query(query_texts=[question], n_results=n_results)
    return results["documents"][0] if results["documents"] else []


if __name__ == "__main__":
    log_customer_interaction("John", "Sent quotation for 25 laptops, awaiting reply.")
    log_customer_interaction("John", "Scheduled a follow-up meeting for Friday 3 PM.")
    print("John's history:", get_customer_history("John"))

    add_knowledge_document("policy-1", "Refunds are processed within 7 business days of request.")
    print("Knowledge query result:", query_knowledge_base("refund policy"))