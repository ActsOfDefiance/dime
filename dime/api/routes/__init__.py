from fastapi import APIRouter

from dime.api.routes.articles import router as articles_router
from dime.api.routes.images import router as images_router
from dime.api.routes.projects import router as projects_router
from dime.api.routes.websocket import router as websocket_router

router = APIRouter()
router.include_router(projects_router)
router.include_router(articles_router)
router.include_router(images_router)
router.include_router(websocket_router)
