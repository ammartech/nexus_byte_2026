from pydantic import BaseModel
from typing import Optional

class TemplateResponse(BaseModel):
    id: str
    name: str
    preview_url: Optional[str] = None