import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.optimization import Optimization
from app.schemas.optimization import OptimizationCreateRequest, OptimizationResponse, OptimizationListItem
from app.core.ai_client import call_with_retry, ats_scorer, content_rewriter, AIServiceTimeout

router = APIRouter(prefix="/api/v1/optimizations", tags=["optimizations"])


@router.post("", response_model=OptimizationResponse, status_code=202)
def create_optimization(
    payload: OptimizationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == payload.document_id, Document.user_id == current_user.id, Document.deleted == False)
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Write the job record BEFORE calling any AI service (per B10 requirement #1)
    job = Optimization(
        id=uuid.uuid4(),
        user_id=current_user.id,
        document_id=document.id,
        status="QUEUED",
        result=None,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    result = {}
    partial = False

    # Call ATS scorer with retry/timeout
    try:
        score_result = call_with_retry("ATSScore", lambda: ats_scorer("mock cv text"))
        result["ats_score"] = score_result
    except AIServiceTimeout:
        result["ats_score"] = {"unavailable": True}
        partial = True

    # Call content rewriter with retry/timeout
    try:
        rewrite_result = call_with_retry("PhraseBoost", lambda: content_rewriter("mock cv text"))
        result["rewrites"] = rewrite_result
    except AIServiceTimeout:
        result["rewrites"] = {"unavailable": True}
        partial = True

    job.status = "PARTIAL" if partial else "COMPLETE"
    job.result = result
    db.commit()
    db.refresh(job)

    return OptimizationResponse(
        id=str(job.id),
        document_id=str(job.document_id),
        status=job.status,
        result=job.result,
    )


@router.get("", response_model=List[OptimizationListItem])
def list_optimizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
):
    jobs = (
        db.query(Optimization)
        .filter(Optimization.user_id == current_user.id)
        .order_by(Optimization.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        OptimizationListItem(id=str(j.id), document_id=str(j.document_id), status=j.status)
        for j in jobs
    ]