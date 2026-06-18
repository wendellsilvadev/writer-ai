import logging
from fastapi import APIRouter, HTTPException
from app.models.predictions import TextPredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService
from app.services.mlflow_service import MLflowService
from app.services.monitoring_service import monitoring_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["predictions"])

mlflow_service = MLflowService()

@router.post("/predict", response_model=PredictionResponse)
async def predict(request: TextPredictionRequest) -> PredictionResponse:
    """
    Realiza predição de sentimento e engajamento.
    
    Args:
        request: Requisição com texto
        
    Returns:
        Resposta com predições
    """
    try:
        # Realizar predição
        prediction = PredictionService.predict(request.texto)
        
        # Log no MLflow
        mlflow_service.log_prediction(request.texto, prediction)
        
        # Log no histórico para monitoramento
        monitoring_service.log_prediction_to_history(request.texto, prediction)
        
        logger.info(f"✅ Predição realizada com sucesso")
        
        return prediction
        
    except RuntimeError as e:
        logger.error(f"❌ Erro: {e}")
        raise HTTPException(
            status_code=503,
            detail="Modelos não carregados. Execute treinamento primeiro."
        )
    except Exception as e:
        logger.error(f"❌ Erro ao processar requisição: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Verifica saúde da API."""
    from app.services.ml_service import ml_service
    
    return {
        "status": "ok",
        "models_loaded": ml_service.is_ready()
    }

@router.get("/drift")
async def get_drift_report(window_size: int = 100):
    """
    Retorna relatório de drift.
    
    Args:
        window_size: Tamanho da janela para análise
        
    Returns:
        Relatório de drift
    """
    return monitoring_service.get_drift_report(window_size)
