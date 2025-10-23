from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
from typing import List

SYNC_FOLDER = "/opt/crdt-cluster/sync_folder/lww"  # Altere para caminho Windows se necessário para testes

router = APIRouter()

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(SYNC_FOLDER, file.filename)
    try:
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        return {"filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/", response_model=List[str])
def list_files():
    try:
        return os.listdir(SYNC_FOLDER)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(SYNC_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

