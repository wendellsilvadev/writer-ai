import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
from app.api import routes, health

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para análise de sentimentos e predição de engajamento"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health.router)
app.include_router(routes.router)

@app.on_event("startup")
async def startup_event():
    """Evento de startup da aplicação."""
    logger.info("🚀 Iniciando Writer AI Backend...")
    logger.info(f"MLflow Tracking URI: {settings.mlflow_tracking_uri}")
    logger.info(f"MinIO Endpoint: {settings.minio_endpoint_url}")
    
    # Verificar carregamento dos modelos
    from app.services.ml_service import ml_service
    if ml_service.is_ready():
        logger.info("✅ Modelos carregados com sucesso!")
    else:
        logger.warning("⚠️ Modelos não carregados. Execute treinamento via ML Pipeline.")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de shutdown da aplicação."""
    logger.info("🛑 Encerrando Writer AI Backend...")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Bem-vindo ao Writer AI",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
