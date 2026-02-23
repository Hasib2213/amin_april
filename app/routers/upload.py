from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.dependencies import get_db, get_current_user_id
from app.services.dna_parser import parse_dna
from app.services.gedcom_parser import parse_gedcom
from app.services.ocr_extractor import extract_from_file
from app.utils.file_handler import save_temp_file
from app.models.upload import DNAUpload, GEDCOMUpload, DocumentUpload, PhotoUpload, DNASNP
from bson import ObjectId
import aiofiles.os
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["upload"])

@router.post("/dna")
async def upload_dna(
    file: UploadFile = File(...), 
    db = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    if not file.filename.lower().endswith(('.txt', '.zip')):
        raise HTTPException(400, "DNA: .txt or .zip only")

    temp_path = await save_temp_file(file)
    try:
        with open(temp_path, "rb") as f:
            content = f.read()
        snps = parse_dna(content, file.filename)

        upload_doc = DNAUpload(
            user_id=user_id,
            filename=file.filename,
            snps=[DNASNP(**s) for s in snps]
        ).dict(exclude_none=True)

        result = await db.uploads.insert_one(upload_doc)
        return {"status": "ok", "id": str(result.inserted_id), "snps": len(snps)}
    finally:
        await aiofiles.os.remove(temp_path)

@router.post("/gedcom")
async def upload_gedcom(
    file: UploadFile = File(...), 
    db = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    if not file.filename.lower().endswith('.ged'):
        raise HTTPException(400, ".ged only")

    temp_path = await save_temp_file(file)
    try:
        parsed = parse_gedcom(temp_path)

        upload_doc = GEDCOMUpload(
            user_id=user_id,
            filename=file.filename,
            individuals=parsed["individuals"],
            families=parsed["families"]
        ).dict()

        result = await db.uploads.insert_one(upload_doc)
        return {"status": "ok", "id": str(result.inserted_id)}
    finally:
        await aiofiles.os.remove(temp_path)

@router.post("/document")
async def upload_document(
    file: UploadFile = File(...), 
    db = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    content = await file.read()
    mime = file.content_type or "application/pdf"

    try:
        extracted = await extract_from_file(content, mime)

        doc = DocumentUpload(
            user_id=user_id,
            filename=file.filename,
            extracted_text=extracted.full_text,
            summary=extracted.summary,
            key_entities=extracted.key_entities
        ).dict()

        result = await db.uploads.insert_one(doc)
        return {"status": "ok", "id": str(result.inserted_id), "extracted": extracted.dict()}
    except Exception as e:
        raise HTTPException(500, f"OCR failed: {str(e)}")

@router.post("/photo")
async def upload_photo(
    file: UploadFile = File(...), 
    db = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    # Validate image file types
    allowed_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(400, "Only image files allowed: JPG, PNG, GIF, BMP, WEBP")
    
    content = await file.read()
    mime = file.content_type or "image/jpeg"

    try:
        extracted = await extract_from_file(content, mime)

        photo = PhotoUpload(
            user_id=user_id,
            filename=file.filename,
            extracted_text=extracted.full_text,
            summary=extracted.summary,
            key_entities=extracted.key_entities
        ).dict()

        result = await db.uploads.insert_one(photo)
        return {"status": "ok", "id": str(result.inserted_id), "extracted": extracted.dict()}
    except Exception as e:
        raise HTTPException(500, f"Photo OCR failed: {str(e)}")