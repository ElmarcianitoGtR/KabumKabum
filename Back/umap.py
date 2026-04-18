from fastapi import APIRouter
from app.services.umap_service import umap_embedding

router = APIRouter(
    prefix="/umap",
    tags=["UMAP"]
)

@router.get("/embedding")
async def get_umap_embedding():
    return {
        "points": umap_embedding
    }