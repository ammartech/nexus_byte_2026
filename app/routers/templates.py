from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.template import Template
from app.schemas.template import TemplateResponse

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])


@router.get("", response_model=List[TemplateResponse])
def list_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    templates = db.query(Template).all()
    return [
        TemplateResponse(id=str(t.id), name=t.name, preview_url=t.preview_url)
        for t in templates
    ]