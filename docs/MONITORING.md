# 👁️ Monitoramento e Observabilidade - Writer AI

## Overview

O monitoramento em Writer AI cobre:

1. **Model Performance**: Acurácia, precisão, recall, F1
2. **Data Drift**: Detecção de mudanças nos dados
3. **API Health**: Latência, erros, uptime
4. **Resource Usage**: CPU, memória, disco
5. **Business Metrics**: Distribuição de sentimentos, engajamento

## MLflow Tracking

### Acessar MLflow UI

http://localhost:5000

### Estrutura no MLflow

```
Experiments
  └─ writer-ai
      ├─ Run 1 (2026-06-17 10:30)
      │  ├─ Parameters
      │  │  ├─ test_size: 0.2
      │  │  ├─ random_state: 42
      │  │  └─ tfidf_max_features: 1000
      │  ├─ Metrics
      │  │  ├─ sentiment_accuracy: 0.82
      │  │  ├─ sentiment_f1_weighted: 0.80
      │  │  ├─ engagement_accuracy: 0.78
      │  │  └─ engagement_f1_weighted: 0.76
      │  └─ Artifacts
      │     ├─ models/sentiment_model.joblib
      │     ├─ models/engagement_model.joblib
      │     ├─ sentiment_evaluation.json
      │     └─ engagement_evaluation.json
      └─ Run 2 (2026-06-18 14:00)
         └─ ...
```

### CLI MLflow

```bash
# List experiments
mlflow experiments list

# Get run details
mlflow runs get --run-id <run_id>

# Delete run
mlflow runs delete --run-id <run_id>

# Download artifact
mlflow artifacts download \
  -u s3://writer-ai/artifacts \
  -d local_dir \
  --artifact-path models
```

## Model Performance Monitoring

### Métricas Primárias

Para **Modelo de Sentimentos** (8 classes):

```json
{
  "accuracy": 0.82,
  "precision_macro": 0.79,
  "precision_weighted": 0.80,
  "recall_macro": 0.78,
  "recall_weighted": 0.82,
  "f1_macro": 0.78,
  "f1_weighted": 0.80
}
```

Para **Modelo de Engajamento** (3 classes):

```json
{
  "accuracy": 0.78,
  "precision_macro": 0.76,
  "precision_weighted": 0.77,
  "recall_macro": 0.75,
  "recall_weighted": 0.78,
  "f1_macro": 0.75,
  "f1_weighted": 0.77
}
```

### Limites de Alerta

```python
ALERTS = {
    "accuracy": {
        "critical": 0.70,  # Parar produção < 70%
        "warning": 0.75    # Notificar < 75%
    },
    "f1_weighted": {
        "critical": 0.68,
        "warning": 0.73
    },
    "data_drift": {
        "critical": 0.30,  # >30% drift
        "warning": 0.15    # >15% drift
    }
}
```

## Data Drift Detection

### O que é Data Drift?

Mudança na distribuição dos dados de entrada ao longo do tempo:

```
Treino (referência)          Produção (6 meses depois)
Positivo: 15%         vs     Positivo: 8%
Negativo: 10%         vs     Negativo: 18%
...
```

### Evidently Dashboard

Acesse: http://localhost:8001

Verifica:
- Distribuição de sentimentos (mudou?)
- Distribuição de comprimento de texto (mudou?)
- Correlação com engajamento (mudou?)

### Implementação

```python
# backend/app/services/monitoring_service.py

class MonitoringService:
    def log_prediction_to_history(self, texto, prediction):
        """Registra predição para análise de drift."""
        self.prediction_history.append({
            "texto_length": len(texto),
            "sentiment": prediction.tom_predominante,
            "engagement": prediction.engajamento,
            "timestamp": now()
        })
    
    def get_drift_report(self, window_size=100):
        """Compara últimas N predições com baseline."""
        baseline = load_baseline_stats()  # Do treinamento
        recent = self.prediction_history[-window_size:]
        
        drift = compare_distributions(baseline, recent)
        
        return {
            "drift_detected": drift > THRESHOLD,
            "drift_score": drift,
            "recommendation": "Retreinar" if drift > THRESHOLD else "OK"
        }
```

### API de Drift

```bash
# GET /api/drift?window_size=100
curl http://localhost:8000/api/drift

# Response
{
  "window_size": 100,
  "mean_sentiment_confidence": 0.78,
  "sentiment_distribution": {
    "positivo": 12,
    "negativo": 8,
    "esperancoso": 25,
    ...
  },
  "drift_detected": false,
  "timestamp": "2026-06-17T10:30:45"
}
```

## API Performance

### Métrica de Latência

Monitore via headers HTTP:

```python
# backend/app/main.py
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

Cliente:
```bash
curl -i http://localhost:8000/api/predict

# Headers
# X-Process-Time: 0.145 (segundos)
```

### Latência por Componente

```
Total: ~150ms
├─ Request overhead: 5ms
├─ Preprocessing: 20ms
├─ TF-IDF transform: 30ms
├─ Sentiment prediction: 40ms
├─ Engagement prediction: 35ms
└─ Response: 5ms
```

### SLA Targets

```yaml
P50 (median):  < 100ms
P95 (95th):    < 200ms
P99 (99th):    < 500ms
Error rate:    < 0.1%
Uptime:        99.9%
```

## Resource Monitoring

### Docker Stats

```bash
# Monitor em tempo real
docker stats

# Exemplo output
CONTAINER          CPU %   MEM USAGE    NET I/O
writer-ai-backend  1.2%    280MB        2MB/1MB
writer-ai-postgres 0.5%    150MB        1MB/500KB
writer-ai-minio    0.3%    200MB        500KB/300KB
```

### Alertas de Recurso

```python
RESOURCE_LIMITS = {
    "memory": {
        "critical": "500MB",  # Parar > 500MB
        "warning": "400MB"    # Alertar > 400MB
    },
    "cpu": {
        "critical": "80%",
        "warning": "60%"
    },
    "disk": {
        "critical": "90%",
        "warning": "70%"
    }
}
```

## Logging Estruturado

### Backend Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info("✅ Predição concluída")
logger.warning("⚠️ Modelo carregado com delay")
logger.error("❌ Erro ao processar: ...")
logger.debug("Sentimentos: {...}")
```

### Log Format

```
2026-06-17 10:30:45,123 - backend.api.routes - INFO - ✅ Predição realizada com sucesso
```

### Log Agregation

Todos os logs vão para:
- **Arquivo**: `backend/logs/`
- **Docker**: `docker compose logs`
- **MLflow**: `mlflow.log_dict(..., "logs.txt")`

### Buscar em Logs

```bash
# Backend
docker compose logs backend | grep ERROR

# Todos os services
docker compose logs | grep "2026-06-17 10:30"

# ML training
tail -f ml/logs/training.log | grep "Accuracy"
```

## Custom Dashboards

### Prometheus Metrics (Exemplo)

```python
from prometheus_client import Counter, Histogram

prediction_counter = Counter(
    'predictions_total',
    'Total predictions',
    ['sentiment', 'engagement']
)

prediction_latency = Histogram(
    'prediction_latency_seconds',
    'Prediction latency'
)

# Uso
prediction_counter.labels(
    sentiment='positivo',
    engagement='alto'
).inc()

prediction_latency.observe(0.145)
```

Metrics endpoint: http://localhost:8000/metrics

### Grafana Dashboard

Configure data source:
```
Type: Prometheus
URL: http://localhost:9090
```

Crie dashboard com queries:
```
# Predictions per minute
rate(predictions_total[1m])

# Latency P95
histogram_quantile(0.95, prediction_latency_seconds)

# Error rate
rate(http_requests_total{status=~"5.."}[5m])
```

## Alerting

### Alertas por Email

```python
import smtplib
from email.mime.text import MIMEText

def send_alert(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = 'noreply@writer-ai.com'
    msg['To'] = 'ops@company.com'
    
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.send_message(msg)
    smtp.quit()

# Uso
if accuracy < CRITICAL_THRESHOLD:
    send_alert(
        "🚨 CRÍTICO: Acurácia muito baixa",
        f"Accuracy: {accuracy:.2%}"
    )
```

### Alertas para Slack

```python
import requests

def send_slack_alert(message):
    requests.post(
        'https://hooks.slack.com/...',
        json={
            'text': message,
            'attachments': [{
                'color': 'danger',
                'title': '⚠️ Writer AI Alert'
            }]
        }
    )
```

## Observability Checklist

- [ ] MLflow Tracking configurado e funcionando
- [ ] PostgreSQL com backups diários
- [ ] MinIO com replicação (produção)
- [ ] Logs centralizados (ELK, Datadog, etc)
- [ ] Métricas de performance (Prometheus)
- [ ] Dashboards (Grafana)
- [ ] Alertas configurados
- [ ] SLOs definidos
- [ ] Runbooks para incidents
- [ ] Postmortems regulares

## Troubleshooting

### "Model accuracy dropped suddenly"

1. Verificar data drift
2. Analisar predições recentes
3. Comparar com baseline
4. Retreinar se necessário

### "API latency increased"

1. Verificar docker stats
2. Verificar I/O disk
3. Verificar conexão PostgreSQL
4. Scale horizontally

### "MLflow database full"

1. Limpar runs antigos
   ```bash
   mlflow runs delete --run-id <id>
   ```
2. Archive runs
3. Aumentar volume PostgreSQL

---

**Monitoramento completo e production-ready**
