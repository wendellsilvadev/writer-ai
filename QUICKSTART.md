# 🚀 QUICKSTART - Writer AI

## ⚡ 3 Passos para Executar

### 1️⃣ Preparar Dataset (1 minuto)

```bash
# Copie o dataset para a pasta correta
cp dataset_sentimentos_500.csv writer-ai/ml/data/raw/

# Verifique se foi copiado
ls writer-ai/ml/data/raw/
# Deve listar: dataset_sentimentos_500.csv
```

### 2️⃣ Iniciar Docker (2 minutos)

```bash
cd writer-ai

# Inicie todos os serviços
docker compose up --build

# Aguarde até ver:
# mlflow_1       | Listening at: http://0.0.0.0:5000
# backend_1      | Uvicorn running on http://0.0.0.0:8000
```

### 3️⃣ Treinar Modelos (3-5 minutos)

Abra outro terminal:

```bash
cd writer-ai

# Execute o treinamento
docker compose exec ml python train.py

# Você verá:
# ✅ Loading dataset...
# ✅ Preprocessing...
# ✅ Training models...
# ✅ Uploading to MinIO...
# ✅ Done!
```

## ✅ Verificação (1 minuto)

### Modelos Treinados?

```bash
# Verifique MLflow
curl http://localhost:5000/api/2.0/experiments/search
```

Esperado: JSON com experimento "writer-ai"

### API Funcionando?

```bash
# Health check
curl http://localhost:8000/health

# Resposta: {"status": "ok"}
```

### Fazer Predição?

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "texto": "A solidão é um silêncio que ecoa dentro de nós com uma voz que nunca aprendemos a escutar."
  }'
```

Resposta esperada:
```json
{
  "sentimentos": {
    "positivo": 0.05,
    "negativo": 0.35,
    ...
  },
  "tom_predominante": "Melancolico",
  "insight": "Uma narrativa intensa e introspectiva...",
  "engajamento": "Alto",
  "confianca_engajamento": 0.89
}
```

## 🌐 Acessar Plataformas

### Frontend (Mesa do Escritor)
👉 **http://localhost**

Escreva um texto e clique "Analisar"

### MLflow (Tracking)
👉 **http://localhost:5000**

Veja métricas de treinamento, modelos, artefatos

### MinIO (S3)
👉 **http://localhost:9001**

- User: `minioadmin`
- Senha: `minioadmin`
- Procure por `writer-ai` bucket → `models` folder

### API Docs
👉 **http://localhost:8000/docs**

Interactive Swagger UI para testar endpoints

## 🆘 Troubleshooting

### "docker: command not found"
→ Instale Docker Desktop https://www.docker.com/products/docker-desktop

### "Connection refused on localhost:8000"
→ Aguarde 30 segundos para backend iniciar
```bash
docker compose logs backend
```

### "Module not found: sklearn"
→ ML não iniciou. Verifique:
```bash
docker compose logs ml
```

### "Cannot find dataset_sentimentos_500.csv"
→ Verifique se copiou para `ml/data/raw/`:
```bash
ls writer-ai/ml/data/raw/dataset_sentimentos_500.csv
```

### "MLflow database error"
→ Limpe e reinicie:
```bash
docker compose down -v
docker compose up --build
```

## 📊 Monitorar Status

```bash
# Ver logs em tempo real
docker compose logs -f

# Ver apenas um serviço
docker compose logs -f backend

# Grep por erros
docker compose logs | grep -i error

# Ver recursos
docker stats
```

## 🧹 Limpeza

```bash
# Parar serviços
docker compose down

# Remover volumes (cuidado!)
docker compose down -v

# Remover tudo (imagens também)
docker compose down -v --rmi all
```

## ✨ Próximos Passos

Após verificação:

1. **Explorar MLflow**: Veja métricas em http://localhost:5000
2. **Testar API**: Use exemplos em `docs/API.md`
3. **Customizar**: Edite `ml/src/config.py` para ajustar hiperparâmetros
4. **Deploy**: Siga `docs/DEPLOYMENT.md` para produção

## 📚 Documentação Completa

- 📖 `docs/README.md` - Visão geral
- 🏗️ `docs/ARCHITECTURE.md` - Arquitetura técnica
- 🔌 `docs/API.md` - API reference completa
- 🎓 `docs/TRAINING.md` - Pipeline ML detalhado
- 🚀 `docs/DEPLOYMENT.md` - Production deployment
- 👁️ `docs/MONITORING.md` - Observabilidade

## 🎯 O que você terá em 10 minutos

✅ Backend FastAPI + 2 modelos ML treinados
✅ Frontend interativa ("Mesa do Escritor")
✅ MLflow tracking com métricas
✅ MinIO com modelos versionados
✅ PostgreSQL com dados
✅ Evidently monitoring setup
✅ 100% pronto para usar

---

**Tempo total: ~10 minutos ⚡**

**Dúvidas? Veja `docs/` ou `PROJECT_SUMMARY.md`**
