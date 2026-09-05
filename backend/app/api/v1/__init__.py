"""
Agrupador de routers de la versión 1 de la API Tracker UP.
"""
from fastapi import APIRouter
from app.api.v1.auth_controller import router as auth_router
from app.api.v1.profile_controller import router as profile_router
from app.api.v1.history_controller import router as history_router
from app.api.v1.metrics_controller import router as metrics_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(profile_router)
api_v1_router.include_router(history_router)
api_v1_router.include_router(metrics_router)

