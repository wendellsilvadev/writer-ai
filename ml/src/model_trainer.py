import logging
import numpy as np
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from src.config import RANDOM_STATE, TEST_SIZE, SENTIMENT_LABELS, ENGAGEMENT_LABELS

logger = logging.getLogger(__name__)

class ModelTrainer:
    """Treina modelos de ML."""
    
    def __init__(self):
        """Inicializa trainer."""
        self.sentiment_model = None
        self.engagement_model = None
    
    def train_sentiment_model(self, X_train, X_test, y_train, y_test):
        """
        Treina modelo de sentimentos (LinearSVC).
        
        Args:
            X_train: Features de treino
            X_test: Features de teste
            y_train: Labels de treino
            y_test: Labels de teste
            
        Returns:
            Dicionários com métricas de treino e teste
        """
        logger.info("\n" + "="*80)
        logger.info("TREINANDO MODELO DE SENTIMENTOS (LinearSVC)")
        logger.info("="*80)
        
        # Treinar modelo
        self.sentiment_model = LinearSVC(
            max_iter=10000,
            random_state=RANDOM_STATE,
            class_weight='balanced',  # Para lidar com desbalanceamento
            dual=False
        )
        
        self.sentiment_model.fit(X_train, y_train)
        logger.info("✅ Modelo LinearSVC treinado")
        
        # Avaliar
        train_score = self.sentiment_model.score(X_train, y_train)
        test_score = self.sentiment_model.score(X_test, y_test)
        
        logger.info(f"Train Accuracy: {train_score:.4f}")
        logger.info(f"Test Accuracy: {test_score:.4f}")
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.sentiment_model, X_train, y_train, 
            cv=5, scoring='accuracy'
        )
        logger.info(f"Cross-Validation Scores: {cv_scores}")
        logger.info(f"Mean CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        return {
            "train_accuracy": train_score,
            "test_accuracy": test_score,
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std()
        }
    
    def train_engagement_model(self, X_train, X_test, y_train, y_test):
        """
        Treina modelo de engajamento (RandomForest).
        
        Args:
            X_train: Features de treino
            X_test: Features de teste
            y_train: Labels de treino
            y_test: Labels de teste
            
        Returns:
            Dicionários com métricas de treino e teste
        """
        logger.info("\n" + "="*80)
        logger.info("TREINANDO MODELO DE ENGAJAMENTO (RandomForest)")
        logger.info("="*80)
        
        # Treinar modelo
        self.engagement_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=RANDOM_STATE,
            n_jobs=-1,
            class_weight='balanced'
        )
        
        self.engagement_model.fit(X_train, y_train)
        logger.info("✅ Modelo RandomForest treinado")
        
        # Avaliar
        train_score = self.engagement_model.score(X_train, y_train)
        test_score = self.engagement_model.score(X_test, y_test)
        
        logger.info(f"Train Accuracy: {train_score:.4f}")
        logger.info(f"Test Accuracy: {test_score:.4f}")
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.engagement_model, X_train, y_train,
            cv=5, scoring='accuracy'
        )
        logger.info(f"Cross-Validation Scores: {cv_scores}")
        logger.info(f"Mean CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # Feature importance
        feature_importance = self.engagement_model.feature_importances_
        top_features_idx = np.argsort(feature_importance)[-10:][::-1]
        logger.info(f"\nTop 10 Features Importance: {feature_importance[top_features_idx]}")
        
        return {
            "train_accuracy": train_score,
            "test_accuracy": test_score,
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std()
        }
