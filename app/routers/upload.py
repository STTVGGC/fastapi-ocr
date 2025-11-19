from fastapi import APIRouter, UploadFile, File
from app.utils.file_utils import save_file
from app.core.config import UPLOAD_DIR
import uuid, os

router = APIRouter(tags=["Upload"])

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    content = await file.read()
    save_file(file_path, content)

    return {"filename": filename, "path": file_path}
