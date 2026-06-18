import logging
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

logger = logging.getLogger(__name__)

class ModelEvaluator:
    """Avalia modelos com métricas detalhadas."""
    
    @staticmethod
    def evaluate_model(y_true, y_pred, model_name: str, labels=None):
        """
        Avalia modelo com métricas completas.
        
        Args:
            y_true: Labels verdadeiros
            y_pred: Labels preditos
            model_name: Nome do modelo
            labels: Nomes das classes
            
        Returns:
            Dicionário com todas as métricas
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"AVALIAÇÃO: {model_name}")
        logger.info(f"{'='*80}\n")
        
        # Accuracy
        accuracy = accuracy_score(y_true, y_pred)
        logger.info(f"Accuracy: {accuracy:.4f}")
        
        # Precision, Recall, F1 (macro e weighted)
        precision_macro = precision_score(y_true, y_pred, average='macro', zero_division=0)
        precision_weighted = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        
        recall_macro = recall_score(y_true, y_pred, average='macro', zero_division=0)
        recall_weighted = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        
        f1_macro = f1_score(y_true, y_pred, average='macro', zero_division=0)
        f1_weighted = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        logger.info(f"\nPrecision (macro): {precision_macro:.4f}")
        logger.info(f"Precision (weighted): {precision_weighted:.4f}")
        
        logger.info(f"\nRecall (macro): {recall_macro:.4f}")
        logger.info(f"Recall (weighted): {recall_weighted:.4f}")
        
        logger.info(f"\nF1-Score (macro): {f1_macro:.4f}")
        logger.info(f"F1-Score (weighted): {f1_weighted:.4f}")
        
        # Confusion Matrix
        cm = confusion_matrix(y_true, y_pred)
        logger.info(f"\nConfusion Matrix:\n{cm}")
        
        # Classification Report
        class_report = classification_report(
            y_true, y_pred, 
            labels=labels if labels else None,
            zero_division=0
        )
        logger.info(f"\nClassification Report:\n{class_report}")
        
        metrics = {
            "accuracy": float(accuracy),
            "precision_macro": float(precision_macro),
            "precision_weighted": float(precision_weighted),
            "recall_macro": float(recall_macro),
            "recall_weighted": float(recall_weighted),
            "f1_macro": float(f1_macro),
            "f1_weighted": float(f1_weighted),
            "confusion_matrix": cm.tolist(),
            "classification_report": class_report
        }
        
        return metrics
