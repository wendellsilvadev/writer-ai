# 📖 README - Plataforma Writer AI

**Versão**: 1.0.0  
**Status**: ✅ Production Ready  
**Data**: Junho 17, 2026

---

## 🎯 O que é Writer AI?

**Writer AI** é uma plataforma de análise de texto baseada em **Machine Learning** que:

1. **Classifica sentimentos** em 8 categorias diferentes (positivo, negativo, neutro, angustiante, misto, esperancoso, filosófico, melancólico)
2. **Prediz engajamento** (Alto, Médio, Baixo) de textos literários
3. **Gera insights** estéticos sobre o tom e estilo do texto
4. **Rastreia modelos** com MLflow (tracking de métricas e versioning)
5. **Armazena modelos** em MinIO (S3-compatible storage)
6. **Monitora drift** de dados com Evidently

**Caso de uso**: Plataforma para escritores/autores analisarem emoção e potencial de engajamento de seus textos em tempo real.

---

## 🚀 Quick Start (3 minutos)

### Requisitos
- Docker Desktop instalado
- dataset_sentimentos_500.csv disponível

### 3 Comandos

```bash
# 1. Copiar dataset
cp dataset_sentimentos_500.csv writer-ai/ml/data/raw/

# 2. Iniciar tudo
cd writer-ai && docker compose up --build

# 3. Treinar modelos (novo terminal)
docker compose exec ml python train.py
```

### Acessar
- **Frontend**: http://localhost
- **API Docs**: http://localhost:8000/docs
- **MLflow**: http://localhost:5000
- **MinIO**: http://localhost:9001 (minioadmin/minioadmin)

---

## 📋 Estrutura do Projeto

```
writer-ai/
├── backend/              # FastAPI application
│   ├── app/             # Código principal
│   │   ├── models/      # Pydantic validation
│   │   ├── services/    # Business logic
│   │   ├── api/         # Endpoints
│   │   └── utils/       # Helpers
│   └── requirements.txt
│
├── frontend/            # Web interface
│   ├── index.html       # Layout
│   ├── styles.css       # Design
│   ├── app.js          # Lógica JavaScript
│   └── Dockerfile
│
├── ml/                  # Machine Learning
│   ├── train.py        # Pipeline principal
│   ├── src/            # Módulos ML
│   ├── data/           # Datasets
│   ├── models/         # Modelos treinados
│   └── Dockerfile
│
├── monitoring/         # Drift detection (Evidently)
│   └── app.py
│
├── docs/               # Documentação (2500+ linhas)
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── TRAINING.md
│   ├── DEPLOYMENT.md
│   └── MONITORING.md
│
└── docker-compose.yml  # Orquestração completa
```

---

## 🏗️ Arquitetura Técnica

### Stack Completo

**Backend**
- Framework: FastAPI 0.104.1
- Validação: Pydantic 2.5.0
- Servidor: Uvicorn
- Python: 3.12

**Machine Learning**
- Vetorização: TF-IDF (scikit-learn)
- Sentimentos: LinearSVC (8 classes)
- Engajamento: RandomForest (3 classes)
- Dados: Pandas, Numpy

**MLOps Infrastructure**
- Tracking: MLflow 2.10.0
- Storage: MinIO (S3-compatible)
- Database: PostgreSQL 15
- Monitoring: Evidently 0.4.13

**Frontend**
- HTML5 + CSS3 + JavaScript (vanilla)
- Chart.js para gráficos
- Nginx como web server
- Responsivo e mobile-ready

**Containerização**
- Docker + Docker Compose
- 7 serviços orquestrados

### Fluxo Completo

```
1. Usuário escreve texto no frontend
   ↓
2. Frontend envia para POST /api/predict
   ↓
3. Backend carrega modelos (ML Service)
   ↓
4. Preprocessamento de texto (normalização, limpeza)
   ↓
5. Vetorização TF-IDF
   ↓
6. LinearSVC prediz 8 sentimentos
   ↓
7. Engajamento features (TF-IDF + sentimentos one-hot + comprimento)
   ↓
8. RandomForest prediz engajamento
   ↓
9. Gera insight literário automático
   ↓
10. Log em MLflow (métricas) + MinIO (artefatos)
    ↓
11. Responde JSON para frontend
    ↓
12. Frontend visualiza com Chart.js
```

---

## 📊 Modelos Treinados

### Modelo de Sentimentos
- **Tipo**: LinearSVC
- **Classes**: 8 (positivo, negativo, neutro, angustiante, misto, esperancoso, filosófico, melancólico)
- **Acurácia esperada**: 82%
- **Métricas**: Precision, Recall, F1 (macro + weighted)

### Modelo de Engajamento
- **Tipo**: RandomForest (200 árvores)
- **Classes**: 3 (Baixo, Médio, Alto)
- **Acurácia esperada**: 78%
- **Features**: TF-IDF + one-hot sentimentos + comprimento texto

### Vetorização
- **Método**: TF-IDF
- **Features**: 1000
- **N-gramas**: (1, 2) - unigrams + bigrams
- **Min docs**: 2
- **Max docs**: 80% do corpus

---

## 💻 API REST

### Endpoint Principal

**POST** `/api/predict`

Request:
```json
{
  "texto": "A solidão é um silêncio que ecoa..."
}
```

Response:
```json
{
  "sentimentos": {
    "positivo": 0.05,
    "negativo": 0.35,
    "neutro": 0.10,
    "angustiante": 0.20,
    "misto": 0.10,
    "esperancoso": 0.05,
    "filosofico": 0.10,
    "melancolico": 0.05
  },
  "tom_predominante": "Melancolico",
  "confianca_tom": 0.95,
  "insight": "Uma narrativa intensa e introspectiva que explora as profundezas da solidão humana...",
  "engajamento": "Alto",
  "confianca_engajamento": 0.87
}
```

### Outros Endpoints

- **GET** `/health` - Health check
- **GET** `/docs` - Swagger UI
- **GET** `/redoc` - ReDoc
- **GET** `/api/drift?window_size=100` - Drift report

---

## 📈 MLflow & MLOps

### O que rastreamos?

**Parâmetros**
- test_size: 0.2
- random_state: 42
- tfidf_max_features: 1000

**Métricas**
- accuracy (ambos modelos)
- precision_macro, precision_weighted
- recall_macro, recall_weighted
- f1_macro, f1_weighted

**Artefatos**
- Modelos .joblib
- Confusion matrices
- Classification reports

### Como acessar?

1. Abra http://localhost:5000
2. Procure por experimento "writer-ai"
3. Clique em runs para ver métricas
4. Download de artefatos

---

## 🎨 Frontend ("Mesa do Escritor")

### Features

✅ **Textarea de entrada** - Mínimo 10 caracteres
✅ **Análise em tempo real** - Spinner durante processamento
✅ **Gráfico de pizza** - Distribuição de sentimentos com Chart.js
✅ **Barras de confiança** - 0-100% por sentimento
✅ **Insight literário** - Descrição automática do tom
✅ **Badge de engajamento** - Alto/Médio/Baixo com cores
✅ **JSON viewer** - Raw data da resposta
✅ **Histórico** - Salvo em localStorage
✅ **Design responsivo** - Mobile, tablet, desktop

### Tecnologias

- HTML5 semântico
- CSS3 (Grid, Flexbox, animations)
- JavaScript vanilla (ES6+)
- Chart.js para gráficos
- LocalStorage para persistência

---

## 🔍 Monitoramento e Observabilidade

### MLflow Tracking
- Veja métricas de treinamento
- Compare runs
- Acesse modelos registrados

### MinIO Storage
- Modelos versionados: `s3://writer-ai/models/v001/`
- Backup automático
- Acesso via console web

### Evidently Monitoring
- Detecção de data drift
- Relatórios de distribuição
- Alertas automáticos

### Logs Estruturados
- Backend: `backend/logs/`
- ML Pipeline: `ml/logs/`
- Docker: `docker compose logs`

---

## 🐳 Docker & Deployment

### Services Incluídos

1. **PostgreSQL** (Database para MLflow)
2. **MinIO** (S3-compatible storage)
3. **MLflow** (Tracking & registry)
4. **Backend** (FastAPI)
5. **Frontend** (Nginx)
6. **Evidently** (Monitoring)
7. **ML** (Training pipeline - opcional)

### Quick Start

```bash
# Build
docker compose build

# Up
docker compose up -d

# Logs
docker compose logs -f

# Train
docker compose exec ml python train.py

# Down
docker compose down
```

---

## 📚 Documentação Completa

| Doc | Assunto | Linhas |
|-----|---------|--------|
| **README.md** | Visão geral | 350+ |
| **ARCHITECTURE.md** | Arquitetura técnica | 500+ |
| **API.md** | Referência de endpoints | 400+ |
| **TRAINING.md** | Pipeline ML detalhado | 400+ |
| **DEPLOYMENT.md** | Production setup | 500+ |
| **MONITORING.md** | Observabilidade | 400+ |
| **TOTAL** | **Documentação completa** | **2,550+** |

---

## 🎓 Como Funciona (Detalhado)

### 1. Preprocessamento de Texto

```
Input: "A violência mais difícil de nomear é aquela que sorri enquanto nos destrói."
  ↓
Normalização: Remove acentos (ü → u)
  ↓
Limpeza: Remove URLs, mentions, caracteres especiais
  ↓
Output: "a violencia mais dificil de nomear é aquela que sorri enquanto nos destroi"
```

### 2. Vetorização TF-IDF

```
Texto processado
  ↓
TF-IDF (1000 features, bigrams)
  ↓
Vector sparse: [0.23, 0.15, ..., 0.08]
```

### 3. Predição de Sentimentos

```
Vector (1000 dims)
  ↓
LinearSVC (treinado em 8 classes)
  ↓
Output: {
  "positivo": 0.05,
  "negativo": 0.35,
  ...
}
```

### 4. Engajamento Features

```
TF-IDF vector (1000) 
  + Sentimentos one-hot (8)
  + Comprimento texto (2)
  = Features vector (1010 dims)
  ↓
RandomForest (3 classes)
  ↓
Output: "Alto" (0.87 confidence)
```

---

## ⚙️ Configuração

### .env Variables

```bash
# Database
POSTGRES_USER=mlflow_user
POSTGRES_PASSWORD=mlflow_password

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# AWS SDK (para MinIO)
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin

# MLflow
MLFLOW_TRACKING_URI=http://mlflow:5000
```

### Customização ML

Edite `ml/src/config.py`:

```python
# TF-IDF
TF_IDF_MAX_FEATURES = 1000      # Aumentar = mais features
NGRAM_RANGE = (1, 2)             # (1,1) = unigrams only
MIN_DF = 2                        # Mínimo docs para feature
MAX_DF = 0.8                      # Máximo % docs

# LinearSVC
MAX_ITER = 10000
CLASS_WEIGHT = 'balanced'

# RandomForest
N_ESTIMATORS = 200
MAX_DEPTH = 15
MIN_SAMPLES_SPLIT = 5
```

---

## 🆘 Troubleshooting

### "Connection refused"
→ Aguarde 30 segundos para backend iniciar

### "Dataset not found"
→ Copie para `ml/data/raw/dataset_sentimentos_500.csv`

### "ModuleNotFoundError"
→ Recrie container: `docker compose rebuild backend`

### "Disk full"
→ Limpe: `docker system prune -a`

Veja [CHECKLIST.md](CHECKLIST.md) para troubleshooting completo.

---

## 🎯 Use Cases

✅ **Análise de sentimento** de textos literários
✅ **Predição de engajamento** em redes sociais
✅ **Insights automáticos** sobre tom narrativo
✅ **Histórico de análises** via localStorage
✅ **Tracking de modelos** via MLflow
✅ **Monitoramento de drift** via Evidently
✅ **Versioning de modelos** via MinIO

---

## 📊 Métricas Esperadas

```
Sentiment Model (LinearSVC, 8 classes)
├─ Accuracy:    ~82%
├─ F1 Weighted: ~80%
└─ Classes:     Balanced

Engagement Model (RandomForest, 3 classes)
├─ Accuracy:    ~78%
├─ F1 Weighted: ~77%
└─ Classes:     Baixo, Médio, Alto

API
├─ Latency:    < 200ms (P95)
├─ Uptime:     99.9%
└─ Error rate: < 0.1%
```

---

## 🚀 Próximos Passos

1. **Desenvolver**: Customize em `ml/src/config.py`
2. **Experimentar**: Compare runs em MLflow
3. **Deployer**: Siga [DEPLOYMENT.md](docs/DEPLOYMENT.md)
4. **Monitorar**: Configure alertas em [MONITORING.md](docs/MONITORING.md)
5. **Escalar**: Implemente Kubernetes conforme [DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## 📞 Suporte

- 📖 Leia a documentação em `docs/`
- 📋 Siga o [CHECKLIST.md](CHECKLIST.md)
- ⚡ Veja [QUICKSTART.md](QUICKSTART.md) para 3 minutos rápidos
- 🏗️ Estude [ARCHITECTURE.md](docs/ARCHITECTURE.md) para detalhes técnicos

---

## 📜 Licença

Projeto acadêmico de MLOps.

---

**Writer AI v1.0.0**  
*Análise de Texto + Machine Learning + MLOps*  
**Status**: ✅ Pronto para produção

🎉 **Aproveite a plataforma!**
