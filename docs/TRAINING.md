# 🤖 Guia de Treinamento - Writer AI

## Visão Geral

O pipeline de treinamento implementa o seguinte fluxo:

```
Dataset (CSV) → Preprocessing → Feature Extraction → Train/Test Split
                                                          ↓
                                    ┌─────────────────────┴──────────────────┐
                                    ↓                                        ↓
                            Sentiment Model (LinearSVC)         Engagement Model (RandomForest)
                                    ↓                                        ↓
                                 Evaluation                                Evaluation
                                    ↓                                        ↓
                                    └─────────────────────┬──────────────────┘
                                                          ↓
                                    MLflow Logging + MinIO Upload → Production
```

## Pré-requisitos

1. **Dataset**: Coloque `dataset_sentimentos_500.csv` em `ml/data/raw/`
2. **Docker**: Docker Compose rodando
3. **Serviços**: PostgreSQL, MinIO, MLflow já iniciados

## Treinamento com Docker

### Quick Start

```bash
# Iniciar todos os serviços
docker compose up -d

# Aguardar que services ficarem healthy (~30s)
sleep 30

# Executar treinamento
docker compose exec ml python train.py
```

### Output Esperado

```
================================================================================
INICIANDO PIPELINE DE TREINAMENTO - WRITER AI
================================================================================

ETAPA 1: Carregando dados...
✅ Arquivo encontrado: /app/ml/data/raw/dataset_sentimentos_500.csv
Dataset carregado: 500 linhas, 8 colunas

ETAPA 2: Preprocessando dados...
Removidas 0 duplicatas
Preprocessando textos...
Categorizando engajamento...
✅ Preprocessamento concluído!

ETAPA 3: Extraindo features...
✅ TF-IDF Vectorizer treinado: (500, 1000)
Vocabulário: 892 features
✅ Label Encoder treinado: 8 classes

ETAPA 4: Dividindo dados...
Treino Sentimentos: (400, 1000), 400
Teste Sentimentos: (100, 1000), 100

ETAPA 5: Treinando modelos...
================================================================================
TREINANDO MODELO DE SENTIMENTOS (LinearSVC)
================================================================================
✅ Modelo LinearSVC treinado
Train Accuracy: 0.8575
Test Accuracy: 0.82
...

ETAPA 6: Avaliando modelos...
...

ETAPA 7: Registrando modelos...
✅ Modelos salvos em: ml/models/
✅ Modelos enviados para S3
✅ Registrados no MLflow

================================================================================
✅ PIPELINE DE TREINAMENTO CONCLUÍDO COM SUCESSO!
================================================================================
```

## Treinamento Local (sem Docker)

### Setup

```bash
cd ml

# Criar virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Colocar dataset em ml/data/raw/
```

### Configurar Variáveis de Ambiente

```bash
# Criar .env na raiz do projeto
export MLFLOW_TRACKING_URI="http://localhost:5000"
export MINIO_ENDPOINT_URL="http://localhost:9000"
export AWS_ACCESS_KEY_ID="minioadmin"
export AWS_SECRET_ACCESS_KEY="minioadmin"
```

### Executar

```bash
python train.py
```

## Arquitetura do Pipeline

### 1. DataLoader

```python
from src.data_loader import DataLoader

loader = DataLoader()
df = loader.load_dataset("dataset_sentimentos_500.csv")
loader.explore_dataset(df)
```

**Output**: DataFrame com 500 linhas, 8 colunas

### 2. DataPreprocessor

```python
from src.preprocessor import DataPreprocessor

preprocessor = DataPreprocessor()
df = preprocessor.preprocess_dataset(df)
```

**Operações**:
- Remove duplicatas
- Remove NaN
- Limpeza de texto (URLs, pontuação, etc)
- Normalização (lowercase, acentos)
- Categoriza engajamento por percentil

**Output**: DataFrame com coluna `trecho_preprocessed` e `engajamento`

### 3. FeatureExtractor

```python
from src.feature_extractor import FeatureExtractor

extractor = FeatureExtractor()

# TF-IDF Vectorization
X_tfidf = extractor.fit_vectorizer(df['trecho_preprocessed'].values)

# Label Encoding
extractor.fit_label_encoder()
y_sentiment = extractor.encode_labels(df['sentimento'].values)

# Features para engajamento
X_engagement = extractor.create_engagement_features(
    X_tfidf, y_sentiment, df['trecho_preprocessed'].values
)
```

**Configuração TF-IDF**:
- max_features: 1000
- ngram_range: (1, 2)
- min_df: 2
- max_df: 0.8

### 4. Train/Test Split

```python
from sklearn.model_selection import train_test_split

# Stratified split para preservar distribuição de classes
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y  # ← IMPORTANTE
)
```

### 5. Model Training

#### Modelo 1: LinearSVC (Sentimentos)

```python
from sklearn.svm import LinearSVC

model = LinearSVC(
    max_iter=10000,
    random_state=42,
    class_weight='balanced',  # Lida com desbalanceamento
    dual=False
)

model.fit(X_train, y_train)
```

**Características**:
- Rápido
- Interpretável
- Bom para multiclasse
- Balanceado automaticamente

#### Modelo 2: RandomForest (Engajamento)

```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)

model.fit(X_train, y_train)
```

**Características**:
- Captura interações não-lineares
- Robuto a outliers
- Feature importance
- Paralelizável

### 6. Model Evaluation

```python
from src.model_evaluator import ModelEvaluator

evaluator = ModelEvaluator()

y_pred = model.predict(X_test)

metrics = evaluator.evaluate_model(
    y_test, y_pred,
    "Sentiment Model",
    labels=SENTIMENT_LABELS
)
```

**Métricas Calculadas**:
- ✅ Accuracy
- ✅ Precision (macro, weighted)
- ✅ Recall (macro, weighted)
- ✅ F1-Score (macro, weighted)
- ✅ Confusion Matrix
- ✅ Classification Report

### 7. MLflow + MinIO Registration

```python
from src.registry_manager import RegistryManager

registry = RegistryManager()
registry.mlflow.start_run("training_run")
registry.mlflow.log_params(params)
registry.mlflow.log_metrics(metrics)

registry.save_and_register_models(
    sentiment_model,
    engagement_model,
    vectorizer,
    label_encoder,
    metrics
)

registry.mlflow.end_run()
```

**Fluxo**:
1. Inicia run no MLflow
2. Log de parâmetros
3. Log de métricas
4. Salva modelos localmente (.joblib)
5. Upload para MinIO/S3
6. Registra no MLflow
7. Finaliza run

## MLflow Web UI

Acesse: http://localhost:5000

### Viewing Training Runs

```
Experiments → writer-ai → [Run Name]
```

Você verá:
- Parâmetros
- Métricas (gráficos)
- Artefatos (models, relatórios)

## MinIO Console

Acesse: http://localhost:9001

**Credentials**: minioadmin / minioadmin

Navegue para: `writer-ai/models/v001/`

Você verá:
```
sentiment_model.joblib
engagement_model.joblib
vectorizer.joblib
label_encoders.joblib
```

## Logs

### Training Log

```bash
tail -f ml/logs/training.log
```

### Docker Logs

```bash
docker compose logs -f ml
```

## Troubleshooting

### "Dataset not found"

```bash
# Verificar localização
ls -la ml/data/raw/

# Copiar dataset se necessário
cp ../dataset_sentimentos_500.csv ml/data/raw/
```

### "MLflow connection failed"

```bash
# Verificar MLflow está rodando
docker compose ps mlflow

# Reconectar
docker compose restart mlflow
docker compose exec ml python train.py
```

### "MinIO connection failed"

```bash
# Verificar MinIO está rodando
docker compose ps minio

# Reconectar
docker compose restart minio
docker compose exec ml python train.py
```

### "Out of memory"

```bash
# Reduzir batch size ou max_features
# Editar ml/src/config.py:
TFIDF_MAX_FEATURES = 500  # de 1000
```

## Métricas Esperadas

Baseado no dataset de 500 amostras:

| Métrica | Esperado |
|---------|----------|
| Sentiment Accuracy | 80-85% |
| Sentiment F1 (weighted) | 78-83% |
| Engagement Accuracy | 75-82% |
| Engagement F1 (weighted) | 73-80% |

## Customização

### Mudar Algoritmo de Sentimentos

```python
# Em model_trainer.py
from sklearn.ensemble import GradientBoostingClassifier

model = GradientBoostingClassifier(n_estimators=200)
```

### Mudar Número de Features TF-IDF

```python
# Em ml/src/config.py
TFIDF_MAX_FEATURES = 2000
```

### Ajustar Hyperparameters

```python
# Em ml/src/model_trainer.py
RandomForestClassifier(
    n_estimators=300,      # aumentar
    max_depth=20,          # aumentar
    min_samples_split=3    # reduzir
)
```

## Reproduibilidade

Para garantir reprodutibilidade:

```bash
# Use random_state fixo
os.environ['PYTHONHASHSEED'] = '42'
np.random.seed(42)
tf.random.set_seed(42)  # se usar TensorFlow

# Estratified split
train_test_split(..., stratify=y)

# Shuffle=False em CV
cross_val_score(..., shuffle=False)
```

## Versionamento de Modelos

Cada treinamento cria:

```
mlflow/
└── runs/
    └── [run_id]/
        ├── models/
        │   ├── sentiment_model.joblib
        │   ├── engagement_model.joblib
        │   └── vectorizer.joblib
        └── metrics.json

s3://writer-ai/
└── models/
    ├── v001/  ← Primeira versão
    ├── v002/  ← Segunda versão
    └── v003/  ← ...
```

## Próximos Passos

1. ✅ Treinar com dataset fornecido
2. ✅ Validar métricas
3. ✅ Testar via API
4. 📊 Monitorar performance em produção
5. 🔄 Retreinar periodicamente com novos dados
6. 📈 Otimizar hyperparameters com Optuna/Ray Tune

---

**Pipeline de treinamento completo e reproducível**
