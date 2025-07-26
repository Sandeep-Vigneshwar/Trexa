from fastapi import APIRouter, Body
from app.services.graph_builder import build_file_tree_graph

router = APIRouter()

@router.post("/graph")
def generate_graph(path: str = Body(..., embed=True)):
    """
    Create and return a file/folder graph structure JSON.
    """
    try:
        graph_data = build_file_tree_graph(path)
        return {"status": "success", "graph": graph_data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
