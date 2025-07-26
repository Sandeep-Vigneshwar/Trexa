from fastapi import APIRouter
from . import search, indexing, graph

router = APIRouter()
router.include_router(search.router, tags=["Search"])
router.include_router(indexing.router, tags=["Indexing"])
router.include_router(graph.router, tags=["Graph"])