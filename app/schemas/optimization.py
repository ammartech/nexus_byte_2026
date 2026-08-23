from pydantic import BaseModel
from typing import Optional, Dict, Any

class OptimizationCreateRequest(BaseModel):
    document_id: str

class OptimizationResponse(BaseModel):
    id: str
    document_id: str
    status: str
    result: Optional[Dict[str, Any]] = None

class OptimizationListItem(BaseModel):
    id: str
    document_id: str
    status: str