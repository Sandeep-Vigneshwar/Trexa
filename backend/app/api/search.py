from fastapi import APIRouter, Query, HTTPException
from app.services.vector_store import search

router = APIRouter()

@router.get("/search")
def search_files(
    query: str = Query(..., min_length=1, description="Search query string"),
    top_k: int = Query(5, ge=1, le=20, description="Number of top results to return")
):
    """
    Perform semantic search on indexed documents.
    """
    try:
        results = search(query, top_k)
        return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
