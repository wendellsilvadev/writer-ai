import logging
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)

class MonitoringService:
    """Serviço para monitoramento e detecção de drift."""
    
    def __init__(self):
        """Inicializa serviço de monitoramento."""
        self.prediction_history = []
    
    def log_prediction_to_history(self, texto: str, prediction):
        """
        Registra predição no histórico para análise de drift.
        
        Args:
            texto: Texto analisado
            prediction: Resultado da predição
        """
        record = {
            "texto_length": len(texto),
            "texto_words": len(texto.split()),
            "sentiment": prediction.tom_predominante,
            "engagement": prediction.engajamento,
            "sentiment_confidence": max(prediction.sentimentos.dict().values()),
            "engagement_confidence": prediction.confianca_engajamento,
            "timestamp": pd.Timestamp.now()
        }
        
        self.prediction_history.append(record)
        logger.debug(f"Predição adicionada ao histórico. Total: {len(self.prediction_history)}")
    
    def get_drift_report(self, window_size: int = 100) -> dict:
        """
        Gera relatório de drift baseado em histórico.
        
        Args:
            window_size: Número de predições para análise
            
        Returns:
            Dicionário com métricas de drift
        """
        if len(self.prediction_history) < window_size:
            logger.warning(f"Histórico insuficiente para análise: {len(self.prediction_history)} < {window_size}")
            return {"status": "insufficient_data"}
        
        df = pd.DataFrame(self.prediction_history[-window_size:])
        
        report = {
            "window_size": window_size,
            "mean_sentiment_confidence": float(df["sentiment_confidence"].mean()),
            "mean_engagement_confidence": float(df["engagement_confidence"].mean()),
            "sentiment_distribution": df["sentiment"].value_counts().to_dict(),
            "engagement_distribution": df["engagement"].value_counts().to_dict(),
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
        logger.info(f"Relatório de drift gerado: {report}")
        
        return report

# Singleton global
monitoring_service = MonitoringService()
