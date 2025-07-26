from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.indexer import index_directory

router = APIRouter()

class IndexRequest(BaseModel):
    folder_path: str

@router.post("/index")
def index_directory_endpoint(body: IndexRequest):
    folder_path = body.folder_path
    if not folder_path:
        raise HTTPException(status_code=400, detail="Missing 'folder_path' in request body")
    index_directory(folder_path)
    return {"status": "success"}