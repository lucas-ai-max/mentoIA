FROM python:3.11-slim

# Configurar Python para não segurar logs (Crucial para debug)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar apenas fastapi e uvicorn (minimalista)
RUN pip install --no-cache-dir fastapi uvicorn

# Copiar código
COPY . .

# Desativar telemetria do CrewAI para evitar travamento no startup
ENV CREWAI_TELEMETRY_OPT_OUT=true
ENV OTEL_SDK_DISABLED=true

# Expor porta
EXPOSE 8080

# Usar main.py minimalista - PORT é definido automaticamente pelo Cloud Run
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1
