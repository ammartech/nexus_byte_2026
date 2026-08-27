import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.core.storage import s3_client, S3_BUCKET
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentDetailResponse

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=422, detail="Unsupported file type")

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 10 MB limit")

    doc_id = uuid.uuid4()
    s3_key = f"{current_user.id}/{doc_id}/{file.filename}"

    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=contents,
        ContentType=file.content_type,
    )

    document = Document(
        id=doc_id,
        user_id=current_user.id,
        filename=file.filename,
        s3_key=s3_key,
        content_type=file.content_type,
        size_bytes=str(len(contents)),
        deleted=False,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return DocumentResponse(
        id=str(document.id),
        filename=document.filename,
        content_type=document.content_type,
        size_bytes=document.size_bytes,
    )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id, Document.deleted == False)
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    download_url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": document.s3_key},
        ExpiresIn=300,
    )

    return DocumentDetailResponse(
        id=str(document.id),
        filename=document.filename,
        content_type=document.content_type,
        size_bytes=document.size_bytes,
        download_url=download_url,
    )


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id, Document.deleted == False)
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.deleted = True
    db.commit()
    return None