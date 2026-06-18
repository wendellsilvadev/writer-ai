import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from src.config import (
    TFIDF_MAX_FEATURES, TFIDF_NGRAM_RANGE,
    TFIDF_MIN_DF, TFIDF_MAX_DF, SENTIMENT_LABELS
)

logger = logging.getLogger(__name__)

class FeatureExtractor:
    """Extrai features dos textos."""
    
    def __init__(self):
        """Inicializa feature extractor."""
        self.vectorizer = None
        self.label_encoder = None
    
    def fit_vectorizer(self, texts):
        """
        Treina vetorizador TF-IDF.
        
        Args:
            texts: Lista de textos
        """
        self.vectorizer = TfidfVectorizer(
            max_features=TFIDF_MAX_FEATURES,
            ngram_range=TFIDF_NGRAM_RANGE,
            min_df=TFIDF_MIN_DF,
            max_df=TFIDF_MAX_DF,
            lowercase=True
        )
        
        X_tfidf = self.vectorizer.fit_transform(texts)
        logger.info(f"✅ TF-IDF Vectorizer treinado: {X_tfidf.shape}")
        logger.info(f"Vocabulário: {len(self.vectorizer.vocabulary_)} features")
        
        return X_tfidf
    
    def transform_texts(self, texts):
        """
        Transforma textos usando vetorizador treinado.
        
        Args:
            texts: Lista de textos
            
        Returns:
            Features TF-IDF
        """
        if self.vectorizer is None:
            raise ValueError("Vectorizer não foi treinado")
        
        return self.vectorizer.transform(texts)
    
    def fit_label_encoder(self):
        """Treina label encoder para sentimentos."""
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(SENTIMENT_LABELS)
        logger.info(f"✅ Label Encoder treinado: {len(SENTIMENT_LABELS)} classes")
    
    def encode_labels(self, labels):
        """
        Codifica labels de sentimentos.
        
        Args:
            labels: Array de sentimentos
            
        Returns:
            Array de labels codificados
        """
        if self.label_encoder is None:
            raise ValueError("Label encoder não foi treinado")
        
        return self.label_encoder.transform(labels)
    
    def decode_labels(self, encoded_labels):
        """
        Decodifica labels para sentiment strings.
        
        Args:
            encoded_labels: Array de labels codificados
            
        Returns:
            Array de sentimentos
        """
        return self.label_encoder.inverse_transform(encoded_labels)
    
    def create_engagement_features(self, X_tfidf, y_sentiment_encoded, texts):
        """
        Cria features para modelo de engajamento.
        
        Args:
            X_tfidf: Features TF-IDF (sparse matrix)
            y_sentiment_encoded: Labels de sentimento codificados
            texts: Textos originais
            
        Returns:
            Features concatenadas para engajamento
        """
        # Converter TF-IDF para denso
        X_tfidf_dense = X_tfidf.toarray()
        
        # One-hot encoding de sentimentos
        n_samples = len(y_sentiment_encoded)
        n_sentiments = len(SENTIMENT_LABELS)
        sentiment_onehot = np.zeros((n_samples, n_sentiments))
        sentiment_onehot[np.arange(n_samples), y_sentiment_encoded] = 1
        
        # Features de comprimento de texto
        text_lengths = np.array([[len(text), len(text.split())] for text in texts])
        
        # Concatenar
        X_engagement = np.hstack([
            X_tfidf_dense,
            sentiment_onehot,
            text_lengths
        ])
        
        logger.info(f"Features de engajamento criadas: {X_engagement.shape}")
        
        return X_engagement
