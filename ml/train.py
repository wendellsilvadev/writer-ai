#!/usr/bin/env python3
"""
Pipeline de treinamento: Writer AI
Treina modelos de sentimentos e engajamento com MLflow + MinIO
"""

import logging
import os
import sys
from pathlib import Path
from sklearn.model_selection import train_test_split
import pandas as pd

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import RANDOM_STATE, TEST_SIZE, SENTIMENT_LABELS, ENGAGEMENT_LABELS
from src.data_loader import DataLoader
from src.preprocessor import DataPreprocessor
from src.feature_extractor import FeatureExtractor
from src.model_trainer import ModelTrainer
from src.model_evaluator import ModelEvaluator
from src.registry_manager import RegistryManager


os.makedirs("logs", exist_ok=True)
# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Executa pipeline completo de treinamento."""
    
    logger.info("\n" + "="*80)
    logger.info("INICIANDO PIPELINE DE TREINAMENTO - WRITER AI")
    logger.info("="*80 + "\n")
    
    try:
        # 1. Carregar dados
        logger.info("ETAPA 1: Carregando dados...")
        data_loader = DataLoader()
        df = data_loader.load_dataset()
        data_loader.explore_dataset(df)
        
        # 2. Preprocessar dados
        logger.info("\n\nETAPA 2: Preprocessando dados...")
        preprocessor = DataPreprocessor()
        df = preprocessor.preprocess_dataset(df)
        
        # 3. Extrair features
        logger.info("\n\nETAPA 3: Extraindo features...")
        feature_extractor = FeatureExtractor()
        
        # TF-IDF
        X_tfidf = feature_extractor.fit_vectorizer(df['trecho_preprocessed'].values)
        
        # Label encoding para sentimentos
        feature_extractor.fit_label_encoder()
        y_sentiment = feature_extractor.encode_labels(df['sentimento'].values)
        
        # Label encoding para engajamento
        le_engagement = LabelEncoder()
        y_engagement = le_engagement.fit_transform(df['engajamento'].values)
        
        # Features para engajamento
        X_engagement = feature_extractor.create_engagement_features(
            X_tfidf, y_sentiment, df['trecho_preprocessed'].values
        )
        
        logger.info(f"Features TF-IDF: {X_tfidf.shape}")
        logger.info(f"Features Engajamento: {X_engagement.shape}")
        
        # 4. Split dados
        logger.info("\n\nETAPA 4: Dividindo dados...")
        
        # Sentimentos
        X_train_sent, X_test_sent, y_train_sent, y_test_sent = train_test_split(
            X_tfidf, y_sentiment, 
            test_size=TEST_SIZE, 
            random_state=RANDOM_STATE,
            stratify=y_sentiment
        )
        
        # Engajamento
        X_train_eng, X_test_eng, y_train_eng, y_test_eng = train_test_split(
            X_engagement, y_engagement,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            stratify=y_engagement
        )
        
        logger.info(f"Treino Sentimentos: {X_train_sent.shape}, {len(y_train_sent)}")
        logger.info(f"Teste Sentimentos: {X_test_sent.shape}, {len(y_test_sent)}")
        logger.info(f"Treino Engajamento: {X_train_eng.shape}, {len(y_train_eng)}")
        logger.info(f"Teste Engajamento: {X_test_eng.shape}, {len(y_test_eng)}")
        
        # 5. Treinar modelos
        logger.info("\n\nETAPA 5: Treinando modelos...")
        trainer = ModelTrainer()
        
        metrics_sentiment = trainer.train_sentiment_model(
            X_train_sent, X_test_sent, y_train_sent, y_test_sent
        )
        
        metrics_engagement = trainer.train_engagement_model(
            X_train_eng, X_test_eng, y_train_eng, y_test_eng
        )
        
        # 6. Avaliar modelos
        logger.info("\n\nETAPA 6: Avaliando modelos...")
        evaluator = ModelEvaluator()
        
        y_pred_sent = trainer.sentiment_model.predict(X_test_sent)
        eval_sentiment = evaluator.evaluate_model(
            y_test_sent, y_pred_sent, 
            "Modelo de Sentimentos",
            labels=list(range(len(SENTIMENT_LABELS)))
        )
        
        y_pred_eng = trainer.engagement_model.predict(X_test_eng)
        eval_engagement = evaluator.evaluate_model(
            y_test_eng, y_pred_eng,
            "Modelo de Engajamento",
            labels=list(range(len(ENGAGEMENT_LABELS)))
        )
        
        # 7. Registrar e salvar
        logger.info("\n\nETAPA 7: Registrando modelos...")
        registry = RegistryManager()
        
        # Iniciar run MLflow
        registry.mlflow.start_run("training_run")
        
        # Log de parâmetros
        params = {
            "test_size": TEST_SIZE,
            "random_state": RANDOM_STATE,
            "tfidf_max_features": 1000,
            "sentiment_model": "LinearSVC",
            "engagement_model": "RandomForestClassifier"
        }
        registry.mlflow.log_params(params)
        
        # Log de métricas
        all_metrics = {
            **{f"sentiment_{k}": v for k, v in eval_sentiment.items() if k != "confusion_matrix" and k != "classification_report"},
            **{f"engagement_{k}": v for k, v in eval_engagement.items() if k != "confusion_matrix" and k != "classification_report"}
        }
        registry.mlflow.log_metrics(all_metrics)
        
        # Log de relatórios
        registry.mlflow.log_dict(eval_sentiment, "sentiment_evaluation.json")
        registry.mlflow.log_dict(eval_engagement, "engagement_evaluation.json")
        
        # Salvar modelos
        registry.save_and_register_models(
            trainer.sentiment_model,
            trainer.engagement_model,
            feature_extractor.vectorizer,
            feature_extractor.label_encoder,
            all_metrics
        )
        
        registry.mlflow.end_run()
        
        logger.info("\n" + "="*80)
        logger.info("✅ PIPELINE DE TREINAMENTO CONCLUÍDO COM SUCESSO!")
        logger.info("="*80)
        logger.info(f"\nModelos salvos em: ml/models/")
        logger.info(f"Logs disponíveis em: ml/logs/training.log")
        logger.info(f"MLflow disponível em: http://localhost:5000")
        
    except Exception as e:
        logger.error(f"\n❌ ERRO NO PIPELINE: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    from sklearn.preprocessing import LabelEncoder
    main()
