import logging
import json
import joblib
from pathlib import Path
import mlflow
import boto3
from src.config import (
    MLFLOW_TRACKING_URI, MLFLOW_EXPERIMENT_NAME,
    MODEL_REGISTRY_STAGE, MODELS_DIR,
    MINIO_ENDPOINT_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
    S3_BUCKET_NAME, SENTIMENT_MODEL_NAME, ENGAGEMENT_MODEL_NAME,
    VECTORIZER_NAME, LABEL_ENCODER_NAME
)

logger = logging.getLogger(__name__)

class MLflowRegistry:
    """Gerencia registro de modelos no MLflow."""
    
    def __init__(self):
        """Inicializa MLflow."""
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
        logger.info(f"✅ MLflow conectado: {MLFLOW_TRACKING_URI}")
    
    def start_run(self, run_name: str = "training_run"):
        """
        Inicia run no MLflow.
        
        Args:
            run_name: Nome da run
        """
        mlflow.start_run(run_name=run_name)
        logger.info(f"✅ MLflow run iniciada: {run_name}")
    
    def log_params(self, params: dict):
        """Log de parâmetros."""
        for key, value in params.items():
            mlflow.log_param(key, value)
        logger.info(f"✅ {len(params)} parâmetros registrados")
    
    def log_metrics(self, metrics: dict, step: int = 0):
        """Log de métricas."""
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                mlflow.log_metric(key, value, step=step)
        logger.info(f"✅ {len([v for v in metrics.values() if isinstance(v, (int, float))])} métricas registradas")
    
    def log_artifact(self, local_path: str, artifact_path: str = None):
        """Log de artefato."""
        mlflow.log_artifact(local_path, artifact_path)
        logger.info(f"✅ Artefato registrado: {local_path}")
    
    def log_dict(self, data: dict, filename: str):
        """Log de dicionário como arquivo."""
        mlflow.log_dict(data, filename)
        logger.info(f"✅ Dicionário registrado: {filename}")
    
    def end_run(self):
        """Finaliza run."""
        mlflow.end_run()
        logger.info("✅ MLflow run finalizada")

class S3Manager:
    """Gerencia armazenamento em MinIO/S3."""
    
    def __init__(self):
        """Inicializa cliente S3."""
        self.s3_client = boto3.client(
            's3',
            endpoint_url=MINIO_ENDPOINT_URL,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        
        # Criar bucket se não existir
        self._ensure_bucket()
        logger.info(f"✅ S3/MinIO conectado: {MINIO_ENDPOINT_URL}")
    
    def _ensure_bucket(self):
        """Cria bucket se não existir."""
        try:
            self.s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
            logger.info(f"Bucket '{S3_BUCKET_NAME}' existe")
        except:
            self.s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
            logger.info(f"✅ Bucket '{S3_BUCKET_NAME}' criado")
    
    def upload_model(self, local_path: str, s3_key: str):
        """
        Upload de modelo para S3.
        
        Args:
            local_path: Caminho local
            s3_key: Chave S3
        """
        try:
            self.s3_client.upload_file(
                local_path,
                S3_BUCKET_NAME,
                s3_key
            )
            logger.info(f"✅ Modelo enviado para S3: {s3_key}")
        except Exception as e:
            logger.error(f"Erro ao enviar para S3: {e}")
            raise
    
    def download_model(self, s3_key: str, local_path: str):
        """
        Download de modelo do S3.
        
        Args:
            s3_key: Chave S3
            local_path: Caminho local
        """
        try:
            self.s3_client.download_file(
                S3_BUCKET_NAME,
                s3_key,
                local_path
            )
            logger.info(f"✅ Modelo baixado do S3: {s3_key}")
        except Exception as e:
            logger.error(f"Erro ao baixar do S3: {e}")
            raise

class RegistryManager:
    """Gerencia registro e armazenamento de modelos."""
    
    def __init__(self):
        """Inicializa managers."""
        self.mlflow = MLflowRegistry()
        self.s3 = S3Manager()
    
    def save_and_register_models(self, 
                                 sentiment_model, 
                                 engagement_model,
                                 vectorizer,
                                 label_encoder,
                                 metrics: dict):
        """
        Salva modelos localmente e registra no MLflow/MinIO.
        
        Args:
            sentiment_model: Modelo de sentimentos
            engagement_model: Modelo de engajamento
            vectorizer: Vetorizador TF-IDF
            label_encoder: Label encoder
            metrics: Dicionário de métricas
        """
        logger.info("\n" + "="*80)
        logger.info("SALVANDO E REGISTRANDO MODELOS")
        logger.info("="*80 + "\n")
        
        # Salvar localmente
        self._save_models_locally(
            sentiment_model, engagement_model,
            vectorizer, label_encoder
        )
        
        # Upload para S3
        self._upload_models_to_s3()
        
        # Registrar no MLflow
        self._register_in_mlflow(metrics)
    
    def _save_models_locally(self, sentiment_model, engagement_model, 
                             vectorizer, label_encoder):
        """Salva modelos em arquivo local."""
        joblib.dump(sentiment_model, MODELS_DIR / f"{SENTIMENT_MODEL_NAME}.joblib")
        joblib.dump(engagement_model, MODELS_DIR / f"{ENGAGEMENT_MODEL_NAME}.joblib")
        joblib.dump(vectorizer, MODELS_DIR / f"{VECTORIZER_NAME}.joblib")
        joblib.dump(label_encoder, MODELS_DIR / f"{LABEL_ENCODER_NAME}.joblib")
        
        logger.info(f"✅ Modelos salvos em: {MODELS_DIR}")
    
    def _upload_models_to_s3(self):
        """Faz upload dos modelos para MinIO/S3."""
        models_to_upload = [
            (SENTIMENT_MODEL_NAME, f"models/v001/{SENTIMENT_MODEL_NAME}.joblib"),
            (ENGAGEMENT_MODEL_NAME, f"models/v001/{ENGAGEMENT_MODEL_NAME}.joblib"),
            (VECTORIZER_NAME, f"models/v001/{VECTORIZER_NAME}.joblib"),
            (LABEL_ENCODER_NAME, f"models/v001/{LABEL_ENCODER_NAME}.joblib"),
        ]
        
        for model_name, s3_key in models_to_upload:
            local_path = MODELS_DIR / f"{model_name}.joblib"
            if local_path.exists():
                self.s3.upload_model(str(local_path), s3_key)
    
    def _register_in_mlflow(self, metrics: dict):
        """Registra modelos e métricas no MLflow."""
        # Log de métricas
        self.mlflow.log_metrics(metrics)
        
        # Log de artefatos
        for model_file in MODELS_DIR.glob("*.joblib"):
            self.mlflow.log_artifact(str(model_file), "models")
