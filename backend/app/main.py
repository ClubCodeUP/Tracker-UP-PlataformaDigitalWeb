"""
Punto de entrada principal de la API RESTful de Tracker UP (FastAPI).
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.init_db import init_database
from app.api.v1 import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización de esquema y datos semilla autocontenidos
    init_database()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "API RESTful autocontenida para la plataforma Tracker UP. "
        "Permite el seguimiento del avance curricular universitario, gestión del historial "
        "y cálculo dinámico de métricas de desempeño académico."
    ),
    lifespan=lifespan
)

# Configuración de CORS dinámico para desarrollo y producción (Netlify / Vercel)
cors_origins = (
    ["*"]
    if settings.CORS_ORIGINS.strip() == "*"
    else [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de rutas v1
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
def root():
    return {
        "sistema": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "estado": "Operativo",
        "dominio_permitido": settings.INSTITUTIONAL_DOMAIN,
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}

