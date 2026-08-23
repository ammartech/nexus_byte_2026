from pydantic import BaseModel

class ExportRequest(BaseModel):
    optimization_id: str
    format: str = "pdf"