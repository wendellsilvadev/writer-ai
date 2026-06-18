import os
from pathlib import Path

# Diretórios
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Criar diretórios se não existirem
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configurações ML
RANDOM_STATE = int(os.getenv("RANDOM_STATE", 42))
TEST_SIZE = float(os.getenv("TEST_SIZE", 0.2))
VAL_SIZE = float(os.getenv("VAL_SIZE", 0.1))

# MLflow
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
MLFLOW_EXPERIMENT_NAME = "writer-ai"
MODEL_REGISTRY_STAGE = os.getenv("MODEL_REGISTRY_STAGE", "Production")

# MinIO/S3
MINIO_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL", "http://minio:9000")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
S3_BUCKET_NAME = "writer-ai"

SENTIMENT_LABELS = [
    "Angustiante",
    "Misto",
    "Esperançoso",
    "Neutro",
    "Filosófico",
    "Melancólico",
    "Positivo",
    "Negativo"
]
# Engagement
ENGAGEMENT_LABELS = ["Baixo", "Médio", "Alto"]
ENGAGEMENT_THRESHOLDS = {
    "Baixo": (0.0, 6.8),
    "Médio": (6.8, 8.5),
    "Alto": (8.5, 10.0)
}

# TF-IDF
TFIDF_MAX_FEATURES = 1000
TFIDF_NGRAM_RANGE = (1, 2)
TFIDF_MIN_DF = 2
TFIDF_MAX_DF = 0.8

# Modelos
SENTIMENT_MODEL_NAME = "sentiment_model"
ENGAGEMENT_MODEL_NAME = "engagement_model"
VECTORIZER_NAME = "vectorizer"
LABEL_ENCODER_NAME = "label_encoders"
