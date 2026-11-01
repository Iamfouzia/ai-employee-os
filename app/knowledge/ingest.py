"""
Phase 7a: Knowledge Ingestion
----------------------------------
Takes company documents (policies, FAQs, product info - plain text for now,
PDF/docx parsing can be added later) and chunks them into pieces small enough
for good retrieval, then stores them in the `company_knowledge` ChromaDB
collection that was already set up in Phase 3 (app/memory/long_term.py).

Chunking strategy: simple fixed-size sliding window with overlap. This is the
standard starting point for RAG - fancier chunking (by heading, by sentence
boundary) can replace this later without touching anything downstream.
"""

from app.memory.long_term import add_knowledge_document

CHUNK_SIZE = 500       # characters per chunk
CHUNK_OVERLAP = 50     # overlap so context isn't lost at chunk boundaries


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    text = text.strip()
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return [c for c in chunks if c]


def ingest_document(doc_name: str, text: str, metadata: dict | None = None) -> int:
    """Chunk a document and store each chunk in the knowledge base.
    Returns the number of chunks stored."""
    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        chunk_id = f"{doc_name}-chunk-{i}"
        chunk_metadata = {"source_doc": doc_name, "chunk_index": i}
        if metadata:
            chunk_metadata.update(metadata)
        add_knowledge_document(chunk_id, chunk, chunk_metadata)
    return len(chunks)


def ingest_file(filepath: str, metadata: dict | None = None) -> int:
    """Read a .txt file from disk and ingest it. (For PDF/docx, extract text
    first with the pdf/docx skill, then pass the extracted text to ingest_document.)"""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    doc_name = filepath.split("/")[-1].split("\\")[-1]  # works on both OS path styles
    return ingest_document(doc_name, text, metadata)


if __name__ == "__main__":
    sample_policy = """
    Refund Policy: Refunds are processed within 7 business days of a valid
    request. Customers must provide the original invoice number. Refunds are
    issued to the original payment method only.

    Leave Policy: Employees are entitled to 14 days of paid annual leave.
    Leave requests must be submitted at least 3 days in advance through the
    HR portal. Sick leave requires a medical certificate for absences longer
    than 2 days.
    """
    n = ingest_document("hr_and_refund_policy", sample_policy)
    print(f"Ingested {n} chunk(s) from sample policy document.")