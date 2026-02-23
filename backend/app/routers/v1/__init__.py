from fastapi import APIRouter
from app.routers.v1.documents import documents_router

v1_router = APIRouter(prefix="/v1", tags=["v1"])
v1_router.include_router(documents_router)

__all__ = ["v1_router"]