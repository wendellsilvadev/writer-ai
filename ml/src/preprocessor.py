import logging
import re
import unicodedata
import pandas as pd
from src.config import ENGAGEMENT_THRESHOLDS, SENTIMENT_LABELS

logger = logging.getLogger(__name__)

class TextPreprocessor:
    """Preprocessamento de texto."""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Remove acentos e converte para minúsculas."""
        nfd = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
        text = text.lower()
        return text
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Remove caracteres especiais."""
        text = re.sub(r'http\S+|www\S+', '', text)
        text = re.sub(r'@\S+|#\S+', '', text)
        text = re.sub(r'[^a-zA-Z0-9\s.!?,\-]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    @staticmethod
    def preprocess_text(text: str) -> str:
        """Pipeline completo de preprocessamento."""
        text = TextPreprocessor.clean_text(text)
        text = TextPreprocessor.normalize_text(text)
        return text

class EngagementCategorizer:
    """Categoriza engajamento baseado em nota."""
    
    @staticmethod
    def categorize_engagement(nota: float) -> str:
        """
        Categoriza nota em classe de engajamento.
        
        Args:
            nota: Valor da nota (5.0-9.9)
            
        Returns:
            Classe de engajamento
        """
        for label, (min_val, max_val) in ENGAGEMENT_THRESHOLDS.items():
            if min_val <= nota < max_val:
                return label
        return "Alto"  # Default para valores > 8.5

class DataPreprocessor:
    """Preprocessador completo de dados."""
    
    @staticmethod
    def preprocess_dataset(df: pd.DataFrame) -> pd.DataFrame:
        """
        Executa pipeline completo de preprocessamento.
        
        Args:
            df: DataFrame original
            
        Returns:
            DataFrame preprocessado
        """
        df = df.copy()
        
        logger.info("Iniciando preprocessamento...")
        
        # 1. Remover duplicatas
        initial_size = len(df)
        df = df.drop_duplicates()
        logger.info(f"Removidas {initial_size - len(df)} duplicatas exatas")
        
        # 2. Remover missing values
        df = df.dropna(subset=['trecho', 'sentimento', 'nota'])
        logger.info(f"Shape após remover NaN: {df.shape}")
        
        # 3. Preprocessar texto
        logger.info("Preprocessando textos...")
        df['trecho_preprocessed'] = df['trecho'].apply(TextPreprocessor.preprocess_text)
        
        # 4. Categorizar engajamento
        logger.info("Categorizando engajamento...")
        df['engajamento'] = df['nota'].apply(EngagementCategorizer.categorize_engagement)
        
        # 5. Verificar distribuição
        logger.info(f"\nDistribuição de sentimentos:\n{df['sentimento'].value_counts()}")
        logger.info(f"\nDistribuição de engajamento:\n{df['engajamento'].value_counts()}")
        
        logger.info("✅ Preprocessamento concluído!")
        
        return df
