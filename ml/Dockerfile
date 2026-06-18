FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código ML
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/models /app/logs /app/data

# Comando padrão (será sobrescrito pelo docker-compose para treinamento)
CMD ["python", "train.py"]
