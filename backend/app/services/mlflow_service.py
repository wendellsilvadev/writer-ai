import logging
import json
from datetime import datetime
import mlflow
from app.config import settings

logger = logging.getLogger(__name__)

class MLflowService:
    """Serviço para integração com MLflow."""
    
    def __init__(self):
        """Inicializa conexão com MLflow."""
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment(settings.mlflow_experiment_name)
    
    def log_prediction(self, texto: str, prediction_response):
        """
        Registra predição no MLflow.
        
        Args:
            texto: Texto analisado
            prediction_response: Response da predição
        """
        try:
            with mlflow.start_run():
                # Log parâmetros
                mlflow.log_param("texto_length", len(texto))
                mlflow.log_param("texto_words", len(texto.split()))
                
                # Log métricas
                mlflow.log_metric("sentiment_confidence", 
                                max(prediction_response.sentimentos.dict().values()))
                mlflow.log_metric("engagement_confidence", 
                                prediction_response.confianca_engajamento)
                
                # Log artefatos
                prediction_dict = prediction_response.dict()
                prediction_dict["timestamp"] = datetime.now().isoformat()
                prediction_dict["texto"] = texto[:100] + "..." if len(texto) > 100 else texto
                
                mlflow.log_dict(prediction_dict, "prediction.json")
                
                logger.info("✅ Predição registrada no MLflow")
                
        except Exception as e:
            logger.error(f"Erro ao registrar predição no MLflow: {e}")
            # Não propagar erro - logging não é crítico
