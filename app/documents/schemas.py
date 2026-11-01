from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    file_url: str
    file_type: str
    extracted_text: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentQueryRequest(BaseModel):
    query: str
    document_ids: Optional[List[int]] = None


class DocumentQueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]


class SearchQueryRequest(BaseModel):
    keyword: str
    limit: int = 10