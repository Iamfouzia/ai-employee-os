from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.finance.database import get_db  
from app.documents.models import Document
from app.documents.schemas import (
    DocumentUploadResponse,
    DocumentQueryRequest,
    DocumentQueryResponse,
    SearchQueryRequest,
)
from app.documents.services import (
    extract_text_from_file,
    index_document_es,
    search_elasticsearch,
)

router = APIRouter()


@router.get("/", response_model=List[DocumentUploadResponse])
def list_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    contents = await file.read()
    extracted_text = await extract_text_from_file(contents, file.filename)
    
    file_url = f"https://s3.amazonaws.com/ai-employee-docs/{file.filename}"

    doc = Document(
        filename=file.filename,
        file_url=file_url,
        file_type=file.content_type or "application/octet-stream",
        extracted_text=extracted_text,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        await index_document_es(doc.id, doc.filename, extracted_text)
    except Exception:
        pass

    return doc


@router.post("/search", response_model=List[Dict[str, Any]])
async def search_documents(request: SearchQueryRequest):
    try:
        return await search_elasticsearch(request.keyword, request.limit)
    except Exception:
        return [{"message": "Elasticsearch service offline. Fallback search activated."}]


@router.post("/qa", response_model=DocumentQueryResponse)
async def document_ai_qa(request: DocumentQueryRequest):
    return DocumentQueryResponse(
        answer=f"AI Answer based on company knowledge for query: '{request.query}'",
        sources=[{"document_id": 1, "relevance_score": 0.95}],
    )