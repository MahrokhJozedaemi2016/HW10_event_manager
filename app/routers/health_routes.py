from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"])
async def health_check():
    """
    Health Check Endpoint
    """
    return {"status": "ok"}
