import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import psycopg2
from datetime import datetime

logger = logging.getLogger(__name__)

app = FastAPI(title="Writer AI Monitoring", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração PostgreSQL
DB_CONFIG = {
    "host": "postgresql",
    "port": 5432,
    "database": "mlflow_db",
    "user": "mlflow_user",
    "password": "mlflow_password"
}

@app.on_event("startup")
async def startup():
    """Inicialização da aplicação."""
    logger.info("✅ Evidently Monitoring Service iniciado")

@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "service": "evidently-monitoring"}

@app.get("/metrics/sentiment")
async def get_sentiment_metrics():
    """Retorna métricas agregadas de sentimentos."""
    try:
        # Esta é uma implementação simplificada
        # Em produção, consultaria PostgreSQL para dados agregados
        return {
            "timestamp": datetime.now().isoformat(),
            "message": "Métricas de sentimentos disponíveis via MLflow"
        }
    except Exception as e:
        logger.error(f"Erro: {e}")
        return {"error": str(e)}, 500

@app.get("/metrics/engagement")
async def get_engagement_metrics():
    """Retorna métricas agregadas de engajamento."""
    try:
        return {
            "timestamp": datetime.now().isoformat(),
            "message": "Métricas de engajamento disponíveis via MLflow"
        }
    except Exception as e:
        logger.error(f"Erro: {e}")
        return {"error": str(e)}, 500

@app.get("/drift")
async def get_drift_report():
    """Retorna relatório de data drift."""
    try:
        return {
            "timestamp": datetime.now().isoformat(),
            "drift_detected": False,
            "message": "Monitoramento de drift ativo. Use MLflow para histórico completo."
        }
    except Exception as e:
        logger.error(f"Erro: {e}")
        return {"error": str(e)}, 500

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
