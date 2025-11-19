from fastapi import APIRouter, UploadFile, File, Query
from app.services.ocr_service import ocr_service

router = APIRouter(tags=["OCR"])

@router.post("/ocr")
async def ocr_api(
    file: UploadFile = File(None),
    filename: str = Query(None)
):
    if file:
        return await ocr_service.process_bytes(await file.read())
    if filename:
        return await ocr_service.process_path(f"uploads/{filename}")
    return {"error": "Upload file or provide filename."}
