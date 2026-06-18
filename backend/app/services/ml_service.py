import logging
import joblib
from typing import Optional
from pathlib import Path
import mlflow
from app.config import settings

logger = logging.getLogger(__name__)

class MLService:
    """Serviço para carregar e gerenciar modelos ML."""
    
    _instance: Optional['MLService'] = None
    
    def __new__(cls):
        """Singleton pattern para garantir uma única instância."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa o serviço ML."""
        if self._initialized:
            return
            
        self.sentiment_model = None
        self.engagement_model = None
        self.vectorizer = None
        self.label_encoder = None
        
        # Conectar ao MLflow
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment(settings.mlflow_experiment_name)
        
        self._initialized = True
        self._load_models()
    
    def _load_models(self):
        """Carrega modelos do diretório local ou do MLflow."""
        try:
            models_dir = Path("/models")
            
            # Tentar carregar modelos locais primeiro
            if models_dir.exists():
                logger.info("Carregando modelos do diretório local...")
                
                sentiment_path = models_dir / "sentiment_model.joblib"
                engagement_path = models_dir / "engagement_model.joblib"
                vectorizer_path = models_dir / "vectorizer.joblib"
                label_encoder_path = models_dir / "label_encoders.joblib"
                
                if sentiment_path.exists():
                    self.sentiment_model = joblib.load(sentiment_path)
                    logger.info("✅ Modelo de sentimentos carregado")
                
                if engagement_path.exists():
                    self.engagement_model = joblib.load(engagement_path)
                    logger.info("✅ Modelo de engajamento carregado")
                
                if vectorizer_path.exists():
                    self.vectorizer = joblib.load(vectorizer_path)
                    logger.info("✅ Vetorizador TF-IDF carregado")
                
                if label_encoder_path.exists():
                    self.label_encoder = joblib.load(label_encoder_path)
                    logger.info("✅ Label encoders carregados")
            
            if not all([self.sentiment_model, self.engagement_model, self.vectorizer]):
                logger.warning("⚠️ Modelos não encontrados localmente. Treinar antes de usar.")
                
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Verifica se todos os modelos estão carregados."""
        return all([
            self.sentiment_model,
            self.engagement_model,
            self.vectorizer,
            self.label_encoder
        ])
    
    def predict_sentiment(self, X_vectorized):
        """
        Prediz sentimentos.
        
        Args:
            X_vectorized: Features vetorizadas (TF-IDF)
            
        Returns:
            Probabilidades para cada sentimento
        """
        if self.sentiment_model is None:
            raise RuntimeError("Modelo de sentimentos não carregado")
        
        # Obter probabilidades
        probs = self.sentiment_model.decision_function(X_vectorized)
        return probs
    
    def predict_engagement(self, X_features):
        """
        Prediz engajamento.
        
        Args:
            X_features: Features (texto vetorizado + sentimento one-hot)
            
        Returns:
            Probabilidades para cada classe de engajamento
        """
        if self.engagement_model is None:
            raise RuntimeError("Modelo de engajamento não carregado")
        
        # Obter probabilidades
        probs = self.engagement_model.predict_proba(X_features)
        return probs

# Singleton global
ml_service = MLService()
