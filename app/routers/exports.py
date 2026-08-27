import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from reportlab.pdfgen import canvas

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.optimization import Optimization
from app.schemas.export import ExportRequest

router = APIRouter(prefix="/api/v1/exports", tags=["exports"])


@router.post("")
def export_optimization(
    payload: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = (
        db.query(Optimization)
        .filter(Optimization.id == payload.optimization_id, Optimization.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Optimization not found")

    if payload.format != "pdf":
        raise HTTPException(status_code=422, detail="Only pdf export is currently supported")

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(50, 800, f"Optimized CV Export — Job {job.id}")
    c.drawString(50, 780, f"Status: {job.status}")

    y = 750
    if job.result:
        ats = job.result.get("ats_score", {})
        score = ats.get("score", "N/A")
        c.drawString(50, y, f"ATS Score: {score}")
        y -= 20

        rewrites = job.result.get("rewrites", {}).get("rewrites", [])
        for r in rewrites:
            c.drawString(50, y, f"- {r}")
            y -= 20

    c.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=optimization_{job.id}.pdf"},
    )