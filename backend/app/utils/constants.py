"""Constantes da aplicação."""

SENTIMENT_LABELS = [
    "positivo",
    "negativo", 
    "neutro",
    "angustiante",
    "misto",
    "esperancoso",
    "filosofico",
    "melancolico"
]

ENGAGEMENT_LABELS = [
    "Baixo",
    "Médio",
    "Alto"
]

# Mapeamento de thresholds para categorização de engajamento
ENGAGEMENT_THRESHOLDS = {
    "Baixo": (0.0, 6.8),
    "Médio": (6.8, 8.5),
    "Alto": (8.5, 10.0)
}
