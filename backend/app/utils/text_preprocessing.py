import re
import unicodedata
from typing import List

def normalize_text(text: str) -> str:
    """
    Normaliza texto removendo acentos e convertendo para minúsculas.
    
    Args:
        text: Texto a normalizar
        
    Returns:
        Texto normalizado
    """
    # Remover acentos
    nfd = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    
    # Converter para minúsculas
    text = text.lower()
    
    return text

def clean_text(text: str) -> str:
    """
    Limpa texto removendo caracteres especiais.
    
    Args:
        text: Texto a limpar
        
    Returns:
        Texto limpo
    """
    # Remover URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # Remover menções e hashtags
    text = re.sub(r'@\S+|#\S+', '', text)
    
    # Remover caracteres especiais mantendo espaços e pontuação básica
    text = re.sub(r'[^a-zA-Z0-9\s.!?,\-]', '', text)
    
    # Remover espaços múltiplos
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def preprocess_text(text: str) -> str:
    """
    Executa pipeline completo de preprocessamento.
    
    Args:
        text: Texto a processar
        
    Returns:
        Texto processado
    """
    text = clean_text(text)
    text = normalize_text(text)
    return text

# Mapeamento de insights literários baseado em sentimentos
SENTIMENT_INSIGHTS = {
    "positivo": "Um texto que irradia esperança e luz, conectando-se com as emoções elevadas do leitor.",
    "negativo": "Uma narrativa que explora as sombras da experiência humana com autenticidade visceral.",
    "neutro": "Um texto objetivo que prioriza a clareza e a informação acima de abstrações emocionais.",
    "angustiante": "Uma exploração profunda da ansiedade e da incerteza que habita a psicologia moderna.",
    "misto": "Uma obra que abraça paradoxos, mostrando a complexidade da condição humana.",
    "esperancoso": "Um texto imbuído de otimismo que alimenta a resiliência do leitor.",
    "filosofico": "Uma reflexão contemplativa que convida a questionar a natureza da existência.",
    "melancolico": "Uma prosa elegante que captura a beleza na tristeza e na perda."
}

def get_insight(sentiment: str) -> str:
    """
    Retorna insight literário baseado no sentimento.
    
    Args:
        sentiment: Sentimento identificado
        
    Returns:
        Insight literário
    """
    sentiment_lower = sentiment.lower()
    return SENTIMENT_INSIGHTS.get(sentiment_lower, "Um texto que evoca múltiplas camadas de significado.")
