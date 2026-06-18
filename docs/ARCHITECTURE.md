# 🏗️ Arquitetura Técnica Detalhada - Writer AI

## Visão Geral

Writer AI é uma plataforma **production-ready** de MLOps baseada em:

- **Monorepo único** com separação clara de responsabilidades
- **Containerização completa** com Docker Compose
- **MLflow + PostgreSQL + MinIO** para ML Governance
- **Frontend responsivo** em HTML/CSS/JavaScript puro
- **Logging estruturado** e monitoramento com Evidently

## Stack Tecnológico

### Backend
- **Framework**: FastAPI + Uvicorn
- **Tipagem**: Pydantic
- **Python**: 3.12

### ML/Data Science
- **Vetorização**: scikit-learn TF-IDF
- **Classificação**: LinearSVC (sentimentos), RandomForest (engajamento)
- **Preprocessing**: Pandas, Numpy
- **Persistência**: Joblib

### MLOps
- **Tracking**: MLflow
- **Registry**: MLflow Model Registry
- **Storage**: MinIO (S3-compatible)
- **Database**: PostgreSQL 15
- **Monitoramento**: Evidently

### Frontend
- **Markup**: HTML5
- **Estilo**: CSS3 (Grid, Flexbox)
- **Interatividade**: JavaScript Vanilla (ES6+)
- **Visualização**: Chart.js
- **Servidor**: Nginx

### Infraestrutura
- **Container**: Docker
- **Orquestração**: Docker Compose
- **Rede**: Docker Bridge Network

## Fluxo de Dados

### 1. Pipeline de Treinamento

```
Raw Dataset (CSV)
    ↓
[Data Loading] → Exploração e validação
    ↓
[Preprocessing]
├── Limpeza de texto
├── Normalização (acentos, case)
├── Tokenização
└── Categorização de engajamento (nota → classe)
    ↓
[Feature Extraction]
├── TF-IDF Vectorization (1000 features, bigrams)
├── Label Encoding (sentimentos)
└── Feature Engineering (comprimento texto)
    ↓
[Data Split] → 80-20 train-test com stratification
    ↓
┌─────────────────────┬─────────────────────┐
↓                     ↓
[Model 1: Sentiment]  [Model 2: Engagement]
LinearSVC             RandomForest
(8 classes)           (3 classes)
    ↓                     ↓
[Evaluation]          [Evaluation]
├─ Accuracy           ├─ Accuracy
├─ Precision (macro)  ├─ Precision (weighted)
├─ Recall (macro)     ├─ Recall (weighted)
├─ F1 (macro)         ├─ F1 (weighted)
├─ Confusion Matrix   ├─ Confusion Matrix
└─ Classification     └─ Classification
  Report                Report
    ↓                     ↓
    └─────────────────────┴─────────────────────┘
         ↓
[MLflow Logging]
├─ Parâmetros
├─ Métricas
└─ Artefatos (models, vectorizers)
     ↓
[MinIO Upload]
└─ Armazenamento em S3-compatible storage
     ↓
[Model Registry]
└─ Production stage
```

### 2. Pipeline de Inferência (Produção)

```
User Input (Frontend)
    ↓
HTTP POST /api/predict {texto: "..."}
    ↓
[Backend API]
├─ Validação (Pydantic)
└─ Carregamento de modelos (cache em memória)
    ↓
[Text Preprocessing]
├─ Limpeza
└─ Normalização
    ↓
[Feature Extraction]
└─ TF-IDF Transform (usando vectorizer treinado)
    ↓
┌──────────────────┬──────────────────┐
↓                  ↓
[Predict Sentiment][Predict Engagement]
├─ Scores         ├─ Class probabilities
└─ Softmax        └─ Confidence
    ↓                  ↓
    └──────────────────┴──────────────────┘
         ↓
[Post-Processing]
├─ Tone = argmax(sentimentos)
├─ Insight = lookup(tone)
├─ Engagement = argmax(probs)
└─ Confidence = max(probs)
    ↓
[Response Building]
{
  sentimentos: {...},
  tom_predominante: "...",
  insight: "...",
  engajamento: "...",
  confianca_engajamento: 0.xx
}
    ↓
[Logging]
├─ MLflow (predição)
├─ Monitoring (drift detection)
└─ History (para análise)
    ↓
HTTP Response 200 OK → Frontend
    ↓
[Visualização]
├─ Gráfico de pizza (Chart.js)
├─ Cards de sentimentos
├─ Indicador de tone
└─ Badge de engajamento
```

## Componentes Principais

### 1. Backend FastAPI (`backend/`)

```
backend/
├── app/
│   ├── main.py              # App FastAPI, routers, startup/shutdown
│   ├── config.py            # Configurações (env vars)
│   │
│   ├── models/
│   │   └── predictions.py   # Pydantic models (Request/Response)
│   │
│   ├── services/
│   │   ├── ml_service.py            # Carregamento de modelos (singleton)
│   │   ├── prediction_service.py    # Orquestração de predição
│   │   ├── mlflow_service.py        # Logging no MLflow
│   │   └── monitoring_service.py    # Histórico para drift
│   │
│   ├── api/
│   │   ├── routes.py        # Endpoint /api/predict
│   │   └── health.py        # Endpoint /health
│   │
│   └── utils/
│       ├── text_preprocessing.py    # Funções de limpeza
│       └── constants.py             # Constantes (labels, etc)
│
├── Dockerfile
├── requirements.txt
└── logs/
```

**Fluxo de requisição**:
1. POST /api/predict recebida
2. Pydantic valida request
3. PredictionService.predict() chamado
4. MLService (singleton) retorna modelos (cache)
5. Texto preprocessado
6. Features extraídas
7. Modelos fazem predição
8. MLflowService loga resultado
9. MonitoringService armazena no histórico
10. Response construída e retornada

### 2. Frontend (`frontend/`)

```
frontend/
├── index.html       # Estrutura HTML + Layout
├── styles.css       # Estilos responsivos (mobile-first)
├── app.js           # Lógica JavaScript (fetch, charts, events)
├── Dockerfile       # Nginx para servir HTML estático
└── [static assets]
```

**Características**:
- Responsive design (mobile, tablet, desktop)
- Real-time character counter
- Chart.js para visualizar distribuição de sentimentos
- localStorage para histórico local
- Error/Success toasts
- Loading spinners

### 3. ML Pipeline (`ml/`)

```
ml/
├── train.py                 # Orquestrador principal
├── src/
│   ├── config.py           # Constantes e caminhos
│   ├── data_loader.py      # Carregamento de CSV
│   ├── preprocessor.py     # Limpeza e categorização
│   ├── feature_extractor.py    # TF-IDF + encoding
│   ├── model_trainer.py    # Treinamento LinearSVC/RF
│   ├── model_evaluator.py  # Cálculo de métricas
│   └── registry_manager.py # MLflow + MinIO
│
├── data/
│   ├── raw/                 # dataset_sentimentos_500.csv
│   └── processed/           # Dados após preprocessing
│
├── models/                  # Artefatos (.joblib)
│   ├── sentiment_model.joblib
│   ├── engagement_model.joblib
│   ├── vectorizer.joblib
│   └── label_encoders.joblib
│
├── logs/
│   └── training.log
│
├── Dockerfile
└── requirements.txt
```

**Fluxo de treinamento**:
```
train.py
  ├─ DataLoader.load_dataset()
  ├─ DataPreprocessor.preprocess_dataset()
  ├─ FeatureExtractor.fit_vectorizer()
  ├─ train_test_split()
  ├─ ModelTrainer.train_sentiment_model()
  ├─ ModelTrainer.train_engagement_model()
  ├─ ModelEvaluator.evaluate_model() [2x]
  ├─ RegistryManager.save_and_register_models()
  │  ├─ Salva localmente (.joblib)
  │  ├─ Upload para MinIO
  │  └─ Log no MLflow
  └─ Status: ✅
```

### 4. Monitoring (`monitoring/`)

FastAPI app que:
- Disponibiliza endpoints para métricas
- Integra com Evidently
- Lê histórico de predições
- Detecta data drift
- Log em PostgreSQL

### 5. Infrastructure (docker-compose.yml)

**Serviços**:

| Service | Image | Port | Deps | Purpose |
|---------|-------|------|------|---------|
| postgresql | postgres:15 | 5432 | - | MLflow backend store |
| minio | minio/minio | 9000 | - | S3-compatible storage |
| mlflow | ghcr.io/mlflow/mlflow | 5000 | pg | Tracking + registry |
| backend | fastapi (build) | 8000 | mlflow | API REST |
| frontend | nginx (build) | 80 | backend | Web UI |
| evidently | fastapi (build) | 8001 | pg | Monitoring |

**Rede**: Docker Bridge Network (todos podem se comunicar via hostname)

**Volumes**:
- `postgres_data`: Persistência PostgreSQL
- `minio_data`: Persistência MinIO
- `mlflow_data`: Cache MLflow
- `./backend:/app`: Live reload
- `./ml/models:/models` (readonly): Modelos compartilhados

## Fluxo de Engajamento

A estratégia de categorização da nota para engajamento é percentil-based:

```
Distribuição Original:
• Min: 5.0
• Max: 9.9
• Média: 7.68
• Mediana: 7.70

Percentis Calculados:
• Q1 (33%): ~6.8
• Q2 (67%): ~8.5

Categorias Finais:
┌─────────────────────────────────┐
│ BAIXO (0.0 - 6.8)     ~33%     │
│ MÉDIO (6.8 - 8.5)     ~34%     │
│ ALTO  (8.5 - 10.0)    ~33%     │
└─────────────────────────────────┘

Aplicado em train.py:
engajamento = categorize_engagement(nota)

Usado em prediction_service.py:
Features = [TF-IDF] + [sentimento_onehot] + [text_length]
↓
RandomForest.predict_proba()
↓
engagement_class = ENGAGEMENT_LABELS[argmax(probs)]
confidence = max(probs)
```

## Métricas Registradas

### Para cada modelo, são registradas:

**Accuracy**
```python
accuracy_score(y_true, y_pred)
```

**Precision**
- Macro: Média simples entre classes
- Weighted: Ponderado pela frequência da classe

**Recall**
- Macro: Média simples entre classes
- Weighted: Ponderado pela frequência da classe

**F1-Score**
- Macro: Média harmônica das precisões/recalls
- Weighted: Ponderado pela frequência

**Confusion Matrix**
- Matriz NxN (N=8 para sentimentos, N=3 para engagement)
- Armazenada como lista em JSON

**Classification Report**
- Precision, recall, F1 por classe
- Suporte (número de amostras)
- Armazenado como string em JSON

## Segurança e Boas Práticas

### ✅ Implementado

- Validação de entrada (Pydantic)
- CORS habilitado (desenvolvimento)
- Logging estruturado
- Separação de responsabilidades
- Singleton pattern para ML Service (evita múltiplos carregamentos)
- Stratified sampling (preserva distribuição de classes)

### ⚠️ Para Produção

- [ ] Autenticação (JWT/OAuth2)
- [ ] Rate limiting (slowapi)
- [ ] TLS/HTTPS
- [ ] Secrets management (AWS Secrets Manager)
- [ ] Database backups
- [ ] Horizontally scaling (Kubernetes)
- [ ] Alerting e auto-remediation

## Performance

### Latência

| Operation | Tempo Estimado |
|-----------|---|
| Load models (1x cold start) | 2-3s |
| Text preprocessing | 10-50ms |
| TF-IDF transform | 20-100ms |
| Model inference | 5-50ms |
| **Total latência (cold)** | **2-3s** |
| **Total latência (warm)** | **50-200ms** |

### Uso de Memória

- Models: ~50MB (all 3)
- Vectorizer: ~20MB
- Backend app: ~200MB
- **Total: ~300MB**

## Escalabilidade

Para aumentar throughput:

1. **Load Balancer**: Adicionar Nginx upstream
2. **Multiple Backend Instances**: `docker compose up --scale backend=3`
3. **Async Inference**: Usar Celery para background jobs
4. **Model Quantization**: Reduzir tamanho dos modelos
5. **GPU Acceleration**: TensorRT ou ONNX

---

**Arquitetura completa e production-ready**
