from pydantic import BaseModel

class DocumentResponse(BaseModel):
    id: str
    filename: str
    content_type: str
    size_bytes: str

class DocumentDetailResponse(BaseModel):
    id: str
    filename: str
    content_type: str
    size_bytes: str
    download_url: str