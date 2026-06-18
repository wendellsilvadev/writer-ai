# 🚀 Deployment e MLOps - Writer AI

## Deployment Local (Development)

### Quick Start

```bash
# 1. Clone ou navegue para o projeto
cd writer-ai

# 2. Copie e configure .env
cp .env.example .env
# Edite .env conforme necessário

# 3. Inicie Docker Compose
docker compose up --build

# 4. Em outro terminal, execute treinamento
docker compose exec ml python train.py

# 5. Acesse
echo "
Frontend:  http://localhost
API Docs:  http://localhost:8000/docs
MLflow:    http://localhost:5000
MinIO:     http://localhost:9001
"
```

### Inicialização Completa

```bash
# Build de todas as imagens (sem cache)
docker compose build --no-cache

# Iniciar em background
docker compose up -d

# Aguardar services ficarem healthy
docker compose exec postgresql pg_isready -U mlflow_user

# Verificar status
docker compose ps

# Ver logs
docker compose logs -f

# Parar
docker compose down

# Limpar tudo (incluindo volumes)
docker compose down -v
```

## Verificação de Saúde

### Health Checks Automáticos

PostgreSQL:
```bash
docker compose ps postgresql
# STATUS: healthy ✅
```

MinIO:
```bash
docker compose ps minio
# STATUS: healthy ✅
```

### Manual Checks

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost/ | head -20

# MLflow
curl http://localhost:5000

# MinIO
aws s3 ls s3://writer-ai \
  --endpoint-url http://localhost:9000 \
  --access-key minioadmin \
  --secret-key minioadmin

# Evidently
curl http://localhost:8001/health
```

## Environment Variables

### .env - Obrigatório

Copie `.env.example` para `.env`:

```bash
# Banco de dados
POSTGRES_USER=mlflow_user
POSTGRES_PASSWORD=mlflow_password
POSTGRES_DB=mlflow_db

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin

# MLflow
MLFLOW_TRACKING_URI=http://mlflow:5000

# Portas
BACKEND_PORT=8000
MLFLOW_PORT=5000
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001
EVIDENTLY_PORT=8001
```

### Environment Vars para Treinamento

```bash
# ml/src/config.py lê automaticamente:
RANDOM_STATE=42              # Para reproducibilidade
TEST_SIZE=0.2                # Proporção teste
MODEL_REGISTRY_STAGE=Production  # MLflow stage
```

## Gerenciamento de Modelos

### Salvando Modelos

Durante treinamento, modelos são salvos em:

1. **Local**: `ml/models/*.joblib`
2. **MLflow**: Registrado como run artifacts
3. **MinIO**: Uploaded para `s3://writer-ai/models/v001/`

### Carregando Modelos

Backend carrega automaticamente:
```python
# backend/app/services/ml_service.py
ml_service = MLService()  # Singleton
ml_service.is_ready()      # True se carregou
```

### Modelo Registry (MLflow)

Acesse: http://localhost:5000 → Models

Registre models como:
- **Staging**: Em teste
- **Production**: Em uso
- **Archived**: Descontinuados

```bash
# CLI MLflow
mlflow models list
mlflow models get-latest-versions sentiment-model
mlflow models set-model-version-tag \
  --name sentiment-model \
  --version 1 \
  --tag production
```

## PostgreSQL

### Conexão

```bash
# CLI psql dentro do container
docker compose exec postgresql psql -U mlflow_user -d mlflow_db

# Query exemplo
SELECT name FROM experiments;
```

### Backup

```bash
# Dump database
docker compose exec postgresql pg_dump \
  -U mlflow_user \
  mlflow_db > backup_mlflow.sql

# Restore
docker compose exec -T postgresql psql \
  -U mlflow_user \
  mlflow_db < backup_mlflow.sql
```

### Persistência

Dados persistem em volume Docker:
```bash
# Ver volumes
docker volume ls | grep writer-ai

# Inspecionar
docker volume inspect writer-ai_postgres_data
```

## MinIO

### Console

http://localhost:9001

**Login**: minioadmin / minioadmin

### CLI (AWS S3 API)

```bash
# Configurar AWS CLI
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
export AWS_S3_ENDPOINT_URL=http://localhost:9000

# List buckets
aws s3 ls --endpoint-url http://localhost:9000

# List objects
aws s3 ls s3://writer-ai/models/v001/ \
  --endpoint-url http://localhost:9000

# Upload file
aws s3 cp model.joblib s3://writer-ai/models/ \
  --endpoint-url http://localhost:9000

# Download file
aws s3 cp s3://writer-ai/models/model.joblib . \
  --endpoint-url http://localhost:9000
```

### Backup Bucket

```bash
# Sync local para S3
aws s3 sync ml/models s3://writer-ai/models/backup/ \
  --endpoint-url http://localhost:9000

# Sync S3 para local
aws s3 sync s3://writer-ai/models/backup/ ml/models_restored/ \
  --endpoint-url http://localhost:9000
```

## Logs e Debugging

### Docker Logs

```bash
# Logs em tempo real
docker compose logs -f

# Logs de um service específico
docker compose logs -f backend
docker compose logs -f ml
docker compose logs -f mlflow

# Últimas 100 linhas
docker compose logs --tail=100 backend

# Grep em logs
docker compose logs | grep ERROR
```

### Arquivo de Logs

```bash
# Treinamento
tail -f ml/logs/training.log

# Backend (dentro do container)
docker compose exec backend tail -f /app/logs/*.log
```

## Performance

### Monitoramento

```bash
# Uso de recursos
docker stats

# CPU, Memória, Rede em tempo real
watch -n 1 docker stats

# Histórico
docker container ls -a  # container ids
docker inspect <container_id> | grep -A 20 Memory
```

### Otimização

```bash
# Limitar memória (docker-compose.yml)
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 500M
        reservations:
          memory: 250M
```

## Horizontally Scaling

### Multiple Backend Instances

```bash
# Scale para 3 instâncias
docker compose up --scale backend=3

# Load balancer via Nginx (adicionar no compose)
services:
  nginx:
    image: nginx:latest
    ports:
      - "8000:8000"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
```

## CI/CD Integration

### GitHub Actions (exemplo)

```yaml
name: ML Pipeline

on: [push]

jobs:
  test-and-deploy:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: password
      
      minio:
        image: minio/minio
        env:
          MINIO_ROOT_USER: admin
          MINIO_ROOT_PASSWORD: password
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker images
        run: docker compose build
      
      - name: Train model
        run: docker compose exec ml python train.py
      
      - name: Test API
        run: |
          docker compose exec backend pytest
      
      - name: Push to registry
        run: |
          docker tag writer-ai-backend:latest registry.com/writer-ai:latest
          docker push registry.com/writer-ai:latest
```

## Production Deployment

### Kubernetes (exemplo)

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: writer-ai-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: writer-ai-backend
  template:
    metadata:
      labels:
        app: writer-ai-backend
    spec:
      containers:
      - name: backend
        image: registry.com/writer-ai-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: MLFLOW_TRACKING_URI
          value: "http://mlflow:5000"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

Deploy:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
```

## Monitoramento em Produção

### Prometheus + Grafana

```bash
# Adicionar à docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### Alertas

```yaml
# prometheus/rules.yml
groups:
  - name: backend
    rules:
      - alert: HighErrorRate
        expr: |
          (sum(rate(http_requests_total{status=~"5.."}[5m])) by (job)
           /
           sum(rate(http_requests_total[5m])) by (job))
          > 0.05
        for: 5m
        annotations:
          summary: "High error rate on {{ $labels.job }}"
```

## Backup e Disaster Recovery

### Strategy

1. **Modelos**: Versionados no MLflow + MinIO
2. **Database**: PostgreSQL volumes + backups diários
3. **Code**: Git repository
4. **Config**: .env (seguro em secrets manager)

### Backup Diário

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)

# Database
docker compose exec -T postgresql pg_dump \
  -U mlflow_user mlflow_db | \
  gzip > backups/mlflow_db_${DATE}.sql.gz

# MinIO
aws s3 sync s3://writer-ai/models \
  backups/models_${DATE}/ \
  --endpoint-url http://localhost:9000

# Cleanup old backups
find backups/ -mtime +7 -delete
```

Crontab:
```bash
0 2 * * * /path/to/backup.sh
```

## Security Best Practices

- [ ] Usar secrets manager (AWS Secrets, Vault)
- [ ] Enable TLS/HTTPS
- [ ] Implementar autenticação (JWT, OAuth)
- [ ] Rate limiting
- [ ] CORS restritivo (prod)
- [ ] Input validation
- [ ] SQL injection prevention (use ORM)
- [ ] Regular security scans
- [ ] Least privilege access
- [ ] Log audit trails

---

**Deployment pronto para produção**
