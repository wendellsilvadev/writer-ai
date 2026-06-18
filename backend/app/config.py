import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configurações globais da aplicação."""
    
    # FastAPI
    app_name: str = "Writer AI"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # MLflow
    mlflow_tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    mlflow_experiment_name: str = "writer-ai"
    
    # MinIO/S3
    minio_endpoint_url: str = os.getenv("MINIO_ENDPOINT_URL", "http://minio:9000")
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
    s3_bucket_name: str = "writer-ai"
    
    # PostgreSQL
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", 5432))
    postgres_user: str = os.getenv("POSTGRES_USER", "mlflow_user")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "mlflow_password")
    postgres_db: str = os.getenv("POSTGRES_DB", "mlflow_db")
    
    # Models
    model_registry_stage: str = "Production"
    random_state: int = 42
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
