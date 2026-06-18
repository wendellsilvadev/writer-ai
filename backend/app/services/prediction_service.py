import logging
import numpy as np
from scipy.special import softmax
from app.services.ml_service import ml_service
from app.utils.text_preprocessing import preprocess_text, get_insight
from app.utils.constants import SENTIMENT_LABELS, ENGAGEMENT_LABELS
from app.models.predictions import SentimentDistribution, PredictionResponse

logger = logging.getLogger(__name__)

class PredictionService:
    """Serviço para realizar predições."""
    
    @staticmethod
    def predict(texto: str) -> PredictionResponse:
        """
        Realiza predição completa de sentimento e engajamento.
        
        Args:
            texto: Texto para análise
            
        Returns:
            PredictionResponse com resultados
        """
        # Verificar se modelos estão carregados
        if not ml_service.is_ready():
            raise RuntimeError("Modelos não carregados. Execute treinamento primeiro.")
        
        # 1. Preprocessar texto
        texto_processado = preprocess_text(texto)
        logger.info(f"Texto processado: {texto_processado[:50]}...")
        
        # 2. Vetorizar com TF-IDF
        X_vectorized = ml_service.vectorizer.transform([texto_processado])
        logger.info(f"Texto vetorizado com forma: {X_vectorized.shape}")
        
        # 3. Predizer sentimentos
        sentiment_scores = ml_service.predict_sentiment(X_vectorized)
        sentiment_probs = softmax(sentiment_scores[0])  # Converter para probabilidades
        
        logger.info(f"Probabilidades de sentimento: {sentiment_probs}")
        
        # 4. Identificar sentimento predominante
        sentiment_classes = list(ml_service.label_encoder.classes_)

        sentiment_idx = np.argmax(sentiment_probs)
        sentiment_predominante = sentiment_classes[sentiment_idx]
        
        # 5. Criar features para modelo de engajamento
        # Concatenar: TF-IDF + probabilidades de sentimento + features de texto
        features_engagement = PredictionService._create_engagement_features(
            X_vectorized, sentiment_probs, texto
        )
        
        # 6. Predizer engajamento
        engagement_probs = ml_service.predict_engagement(features_engagement)
        engagement_class_idx = np.argmax(engagement_probs[0])
        engagement_class = ENGAGEMENT_LABELS[engagement_class_idx]
        engagement_confidence = float(engagement_probs[0][engagement_class_idx])
        
        logger.info(f"Engajamento: {engagement_class} (confiança: {engagement_confidence:.2%})")
        
        # 7. Criar resposta
        sentimentos_dict = {
            sentiment_classes[i]: float(sentiment_probs[i])
            for i in range(len(sentiment_classes))
        }

        response = PredictionResponse(
            sentimentos=SentimentDistribution(
                positivo=sentimentos_dict.get("Positivo", 0.0),
                negativo=sentimentos_dict.get("Negativo", 0.0),
                neutro=sentimentos_dict.get("Neutro", 0.0),
                angustiante=sentimentos_dict.get("Angustiante", 0.0),
                misto=sentimentos_dict.get("Misto", 0.0),
                esperancoso=sentimentos_dict.get("Esperançoso", 0.0),
                filosofico=sentimentos_dict.get("Filosófico", 0.0),
                melancolico=sentimentos_dict.get("Melancólico", 0.0)
            ),
            tom_predominante=sentiment_predominante,
            insight=get_insight(sentiment_predominante),
            engajamento=engagement_class,
            confianca_engajamento=engagement_confidence
        )

        return response
    
    @staticmethod
    def _create_engagement_features(X_vectorized, sentiment_probs, texto):
        """
        Cria features para o modelo de engajamento.
        
        Args:
            X_vectorized: Features TF-IDF (sparse matrix)
            sentiment_probs: Probabilidades de sentimento (array)
            texto: Texto original
            
        Returns:
            Features concatenadas (array denso)
        """
        # Converter TF-IDF para denso e pegar primeira linha
        tfidf_dense = X_vectorized.toarray()[0]
        
        # Features de texto
        text_length_chars = len(texto)
        text_length_words = len(texto.split())
        
        # Concatenar features
        features = np.concatenate([
            tfidf_dense,
            sentiment_probs,
            [text_length_chars, text_length_words]
        ])
        
        return features.reshape(1, -1)
