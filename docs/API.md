# 📚 API Reference - Writer AI

## Base URL

```
http://localhost:8000
```

## Authentication

Atualmente sem autenticação. Para produção, implemente JWT.

## Endpoints

### 1. POST /api/predict

Realiza predição de sentimento e engajamento para um texto.

**Request**:
```http
POST /api/predict
Content-Type: application/json

{
  "texto": "string (min 10 chars, max 500 chars)"
}
```

**Parameters**:
- `texto` (required, string): Texto para análise
  - Mínimo: 10 caracteres
  - Máximo: 500 caracteres

**Response** (200 OK):
```json
{
  "sentimentos": {
    "positivo": 0.15,
    "negativo": 0.08,
    "neutro": 0.05,
    "angustiante": 0.25,
    "misto": 0.12,
    "esperancoso": 0.20,
    "filosofico": 0.10,
    "melancolico": 0.05
  },
  "tom_predominante": "esperancoso",
  "insight": "Um texto imbuído de otimismo que alimenta a resiliência do leitor.",
  "engajamento": "Alto",
  "confianca_engajamento": 0.92
}
```

**Response Fields**:

- `sentimentos` (object): Distribuição de probabilidades para cada sentimento
  - `positivo` (float, 0-1): Probabilidade de sentimento positivo
  - `negativo` (float, 0-1): Probabilidade de sentimento negativo
  - `neutro` (float, 0-1): Probabilidade de sentimento neutro
  - `angustiante` (float, 0-1): Probabilidade de sentimento angustiante
  - `misto` (float, 0-1): Probabilidade de sentimento misto
  - `esperancoso` (float, 0-1): Probabilidade de sentimento esperançoso
  - `filosofico` (float, 0-1): Probabilidade de sentimento filosófico
  - `melancolico` (float, 0-1): Probabilidade de sentimento melancólico

- `tom_predominante` (string): Sentimento com maior probabilidade
  - Valores: "positivo", "negativo", "neutro", "angustiante", "misto", "esperancoso", "filosofico", "melancolico"

- `insight` (string): Descrição estética/literária do texto baseada no sentimento predominante

- `engajamento` (string): Predição de engajamento
  - Valores: "Alto", "Médio", "Baixo"

- `confianca_engajamento` (float, 0-1): Confiança da predição de engajamento

**Error Responses**:

```json
// 400 Bad Request
{
  "detail": [
    {
      "loc": ["body", "texto"],
      "msg": "ensure this value has at least 10 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

```json
// 503 Service Unavailable
{
  "detail": "Modelos não carregados. Execute treinamento primeiro."
}
```

```json
// 500 Internal Server Error
{
  "detail": "Erro interno: ..."
}
```

**Example (cURL)**:
```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "texto": "A cura não é ausência de cicatriz. É a prova de que sobrevivemos."
  }' | jq
```

**Example (Python)**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/predict",
    json={"texto": "Seu texto aqui..."}
)

result = response.json()
print(f"Tone: {result['tom_predominante']}")
print(f"Engagement: {result['engajamento']}")
```

**Example (JavaScript)**:
```javascript
fetch('http://localhost:8000/api/predict', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    texto: "Seu texto aqui..."
  })
})
.then(r => r.json())
.then(data => {
  console.log('Tone:', data.tom_predominante);
  console.log('Engagement:', data.engajamento);
});
```

---

### 2. GET /health

Health check da API.

**Response** (200 OK):
```json
{
  "status": "ok",
  "models_loaded": true
}
```

**Example**:
```bash
curl http://localhost:8000/health | jq
```

---

### 3. GET /drift

Retorna relatório de drift baseado no histórico de predições.

**Parameters**:
- `window_size` (optional, integer): Número de predições para análise (default: 100)

**Response** (200 OK):
```json
{
  "window_size": 100,
  "mean_sentiment_confidence": 0.78,
  "mean_engagement_confidence": 0.85,
  "sentiment_distribution": {
    "positivo": 10,
    "negativo": 8,
    "esperancoso": 20,
    ...
  },
  "engagement_distribution": {
    "Alto": 72,
    "Médio": 20,
    "Baixo": 8
  },
  "timestamp": "2026-06-17T10:30:45.123456"
}
```

**Example**:
```bash
curl "http://localhost:8000/drift?window_size=50" | jq
```

---

### 4. GET /

Root endpoint com informações da API.

**Response** (200 OK):
```json
{
  "message": "Bem-vindo ao Writer AI",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

## Interactive Documentation

FastAPI gera documentação automática:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Rate Limiting

Não implementado no momento. Para produção, adicione:
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

## CORS

CORS habilitado para todas as origens (desenvolvimento).

Para produção, configure:
```python
CORSMiddleware(
    allow_origins=["https://yourdomain.com"],
    ...
)
```

## Versioning

API atualmente em v1 (path `/api`).

Para versioning futuro:
```
/api/v1/predict
/api/v2/predict
```

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Sucesso |
| 400 | Bad Request - Validação falhou |
| 422 | Unprocessable Entity - Erro de tipo/formato |
| 500 | Internal Server Error - Erro do servidor |
| 503 | Service Unavailable - Modelos não carregados |

## Timestamps

Todos os timestamps são em ISO 8601 UTC:
```
2026-06-17T10:30:45.123456
```

## Limits

- Texto máximo: 500 caracteres
- Histórico de drift: últimas 100 predições por padrão
- Timeout: 30 segundos

## Exemplos de Sentimentos

```
Positivo:     "Que dia lindo e maravilhoso!"
Negativo:     "Que horror e desgosto!"
Neutro:       "O relógio marca 3 horas."
Angustiante:  "Sinto o pânico me sufocando..."
Misto:        "Alegria e tristeza em um só coração..."
Esperançoso:  "Há sempre uma chance de recomeço..."
Filosófico:   "O que é o ser?
Melancólico:  "Os dias passam como folhas no vento..."
```

---

**API pronta para produção**
