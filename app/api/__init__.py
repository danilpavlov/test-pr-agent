from fastapi import APIRouter

from app.api.books import router as books_router

router = APIRouter(prefix="/api")

router.include_router(books_router)

__all__ = ["router"]
