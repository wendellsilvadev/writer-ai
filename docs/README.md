## 📄 Entrega

- 📘 **Documentação Final:** https://docs.google.com/document/d/1SWu6mdsRBQOImlT0wPzxlGscVVOILiaFgVDWDsT_hQ8/edit?tab=t.0#heading=h.9jl3gojm4fao
- 🎥 **Vídeo de Demonstração:** https://...

# 📖 Writer AI - Plataforma de Análise Inteligente de Sentimentos

**Writer AI** é uma plataforma **end-to-end** de Machine Learning + MLOps para análise de sentimentos e predição de engajamento em textos, especialmente otimizada para conteúdo literário.

## ✨ Funcionalidades Principais

- 🎯 **Classificação de 8 Sentimentos**: Positivo, Negativo, Neutro, Angustiante, Misto, Esperançoso, Filosófico, Melancólico
- 📊 **Predição de Engajamento**: Alto, Médio, Baixo
- 💡 **Insights Literários**: Análise estética do texto com base em sentimentos
- 📈 **Dashboard em Tempo Real**: Interface intuitiva "Mesa do Escritor"
- 🔬 **MLflow Integration**: Tracking, registry e versionamento de modelos
- 💾 **MinIO S3 Storage**: Armazenamento seguro de artefatos
- 👁️ **Evidently Monitoring**: Detecção de data drift e monitoramento de performance
- 🐳 **Docker Compose**: Deploy completo em um único comando

## 🏗️ Arquitetura

```
writer-ai/ (Monorepo)
├── backend/           # FastAPI + Pydantic
├── frontend/          # HTML/CSS/JavaScript Vanilla
├── ml/               # Pipeline de treinamento
├── monitoring/       # Evidently + Drift Detection
├── docs/             # Documentação
├── docker-compose.yml
└── .env.example
```

### Serviços

| Serviço | Porta | Tecnologia | Descrição |
|---------|-------|-----------|-----------|
| **Backend API** | 8000 | FastAPI | API REST para predições |
| **Frontend** | 80 | Nginx | Interface web (HTML/CSS/JS) |
| **MLflow** | 5000 | MLflow | Tracking e registry de modelos |
| **PostgreSQL** | 5432 | PostgreSQL 15 | Backend store do MLflow |
| **MinIO** | 9000/9001 | MinIO | S3-compatible storage |
| **Evidently** | 8001 | FastAPI | Monitoramento de drift |

## 🚀 Quick Start

### Pré-requisitos

- Docker & Docker Compose
- Python 3.12+ (para desenvolvimento local)
- Git

### Instalação e Execução

1. **Clone o repositório**
   ```bash
   cd writer-ai
   ```

2. **Configure variáveis de ambiente**
   ```bash
   cp .env.example .env
   ```

3. **Inicie todos os serviços**
   ```bash
   docker compose up --build
   ```

4. **Acesse a plataforma**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - MLflow: http://localhost:5000
   - MinIO Console: http://localhost:9001
   - Evidently: http://localhost:8001

### Primeiros Passos

#### 1. Preparar Dataset
Coloque o arquivo `dataset_sentimentos_500.csv` em `ml/data/raw/`

#### 2. Treinar Modelos
```bash
# Com Docker
docker compose exec ml python train.py

# Ou localmente
cd ml
python train.py
```

#### 3. Usar a API
```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{"texto": "A violência mais difícil de nomear é aquela que sorri enquanto nos destrói."}'
```

Resposta:
```json
{
  "sentimentos": {
    "positivo": 0.05,
    "negativo": 0.45,
    "neutro": 0.10,
    "angustiante": 0.25,
    "misto": 0.05,
    "esperancoso": 0.05,
    "filosofico": 0.03,
    "melancolico": 0.02
  },
  "tom_predominante": "negativo",
  "insight": "Uma narrativa que explora as sombras da experiência humana com autenticidade visceral.",
  "engajamento": "Alto",
  "confianca_engajamento": 0.87
}
```

## 📊 Modelos e Algoritmos

### Modelo 1: Classificação de Sentimentos (8 classes)
- **Algoritmo**: LinearSVC
- **Vetorização**: TF-IDF (1000 features, bigrams)
- **Métrica**: F1-Score Weighted

### Modelo 2: Predição de Engajamento (3 classes)
- **Algoritmo**: RandomForestClassifier (200 árvores)
- **Features**: TF-IDF + One-hot Sentimentos + Comprimento de Texto
- **Métrica**: F1-Score Weighted

## 📈 Métricas Registradas no MLflow

Para cada modelo, as seguintes métricas são registradas:

- ✅ Accuracy
- ✅ Precision (Macro e Weighted)
- ✅ Recall (Macro e Weighted)
- ✅ F1-Score (Macro e Weighted)
- ✅ Confusion Matrix (8x8 e 3x3)
- ✅ Classification Report (detalhado)

## 💾 Armazenamento de Artefatos

### Local (`ml/models/`)
```
models/
├── sentiment_model.joblib      # LinearSVC treinado
├── engagement_model.joblib     # RandomForest treinado
├── vectorizer.joblib           # TF-IDF Vectorizer
└── label_encoders.joblib       # Label encoders
```

### MinIO S3 (`s3://writer-ai/`)
```
s3://writer-ai/
├── models/v001/
│   ├── sentiment_model.joblib
│   ├── engagement_model.joblib
│   ├── vectorizer.joblib
│   └── label_encoders.joblib
└── artifacts/
    └── YYYYMMDD_HHMMSS/
        ├── training_log.txt
        ├── confusion_matrix.png
        └── classification_report.json
```

## 📚 Documentação

- [Arquitetura Detalhada](./docs/ARCHITECTURE.md)
- [API Reference](./docs/API.md)
- [Guia de Treinamento](./docs/TRAINING.md)
- [Deploy e MLOps](./docs/DEPLOYMENT.md)
- [Monitoramento](./docs/MONITORING.md)

## 🔧 Variáveis de Ambiente

Veja `.env.example` para todas as configurações disponíveis.

Principais:
```bash
MLFLOW_TRACKING_URI=http://mlflow:5000
MINIO_ENDPOINT_URL=http://minio:9000
POSTGRES_USER=mlflow_user
POSTGRES_PASSWORD=mlflow_password
```

## 📁 Estrutura de Diretórios

```
writer-ai/
├── backend/
│   ├── app/
│   │   ├── models/          # Pydantic models
│   │   ├── services/        # Lógica de negócio
│   │   ├── api/             # Endpoints FastAPI
│   │   ├── utils/           # Funções auxiliares
│   │   ├── config.py        # Configurações
│   │   ├── main.py          # App FastAPI
│   │   └── __init__.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── logs/
│
├── frontend/
│   ├── index.html           # HTML principal
│   ├── styles.css           # Estilos
│   ├── app.js               # Lógica JavaScript
│   ├── Dockerfile
│   └── Dockerfile
│
├── ml/
│   ├── src/
│   │   ├── config.py        # Configurações ML
│   │   ├── data_loader.py   # Carregamento de dados
│   │   ├── preprocessor.py  # Limpeza de texto
│   │   ├── feature_extractor.py  # TF-IDF
│   │   ├── model_trainer.py # Treinamento
│   │   ├── model_evaluator.py   # Avaliação
│   │   └── registry_manager.py  # MLflow + MinIO
│   ├── data/
│   │   ├── raw/             # Dados brutos
│   │   └── processed/       # Dados processados
│   ├── models/              # Artefatos
│   ├── logs/                # Logs
│   ├── train.py             # Script de treinamento
│   ├── requirements.txt
│   ├── Dockerfile
│   └── notebooks/
│
├── monitoring/
│   ├── app.py               # FastAPI Evidently
│   ├── reports/             # Relatórios de drift
│   ├── requirements.txt
│   └── Dockerfile
│
├── docs/
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── TRAINING.md
│   ├── DEPLOYMENT.md
│   └── MONITORING.md
│
├── docker-compose.yml       # Orquestração completa
├── .env.example             # Configurações
├── .gitignore
└── README.md
```

## 🧪 Teste a API

### Endpoint: POST /api/predict

**Request:**
```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "texto": "A cura não é ausência de cicatriz. É a prova de que sobrevivemos."
  }'
```

**Response:**
```json
{
  "sentimentos": {
    "positivo": 0.42,
    "negativo": 0.08,
    ...
  },
  "tom_predominante": "esperancoso",
  "insight": "Um texto imbuído de otimismo que alimenta a resiliência do leitor.",
  "engajamento": "Alto",
  "confianca_engajamento": 0.92
}
```

## 🔐 Segurança

- Credenciais armazenadas em `.env` (não versionado)
- CORS habilitado para desenvolvimento
- TLS recomendado para produção
- Rate limiting não implementado (adicione conforme necessário)

## 📝 Logs

Logs disponíveis em:
- Backend: `backend/logs/`
- ML: `ml/logs/training.log`
- Docker: `docker compose logs -f [service]`

## 🚫 Troubleshooting

### "Models not loaded"
```bash
# Treinar modelos
docker compose exec ml python train.py
```

### Conexão MinIO falha
```bash
# Verificar se MinIO está rodando
docker compose ps

# Reiniciar MinIO
docker compose restart minio
```

### PostgreSQL não conecta
```bash
# Verificar logs
docker compose logs postgresql

# Resetar volume
docker compose down -v
docker compose up -d
```

## 📄 Licença

Este projeto é fornecido como está para fins educacionais e acadêmicos.

## 👨‍💻 Desenvolvimento

### Desenvolvimento Local (sem Docker)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# ML
cd ml
pip install -r requirements.txt
python train.py

# Frontend
# Servir com live-server ou outro servidor HTTP local
```

### Contribuindo

1. Crie uma branch para sua feature
2. Commit suas mudanças
3. Push para a branch
4. Abra um Pull Request

## 📞 Contato e Suporte

Para dúvidas sobre a arquitetura ou implementação, consulte a documentação em `docs/`.

---

**Made with ❤️ by Senior ML Architect**

Última atualização: Junho 2026
