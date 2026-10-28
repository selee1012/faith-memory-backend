from fastapi import APIRouter

from app.domains.consents.router import router as consents_router
from app.domains.journals.router import router as journals_router
from app.domains.memories.router import router as memories_router
from app.domains.reflections.router import router as reflections_router
from app.domains.search.router import router as search_router
from app.domains.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(users_router)
api_router.include_router(consents_router)
api_router.include_router(journals_router)
api_router.include_router(memories_router)
api_router.include_router(search_router)
api_router.include_router(reflections_router)
