from pydantic import BaseModel, Field

class TextPredictionRequest(BaseModel):
    """Modelo de requisição para predição."""
    texto: str = Field(..., min_length=10, max_length=500, description="Texto para análise")

class SentimentDistribution(BaseModel):
    """Distribuição de sentimentos."""
    positivo: float
    negativo: float
    neutro: float
    angustiante: float
    misto: float
    esperancoso: float
    filosofico: float
    melancolico: float

class PredictionResponse(BaseModel):
    """Modelo de resposta de predição."""
    sentimentos: SentimentDistribution
    tom_predominante: str = Field(..., description="Sentimento com maior probabilidade")
    insight: str = Field(..., description="Análise estética/literária do texto")
    engajamento: str = Field(..., description="Predição de engajamento: Alto, Médio, Baixo")
    confianca_engajamento: float = Field(..., ge=0.0, le=1.0, description="Confiança da predição de engajamento")
