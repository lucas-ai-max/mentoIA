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

# Instalar uv e dependências
RUN pip install uv
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Copiar código
COPY . .

# Desativar telemetria do CrewAI para evitar travamento no startup
ENV CREWAI_TELEMETRY_OPT_OUT=true
ENV OTEL_SDK_DISABLED=true

# Expor porta
EXPOSE 8080

# Tornar o entrypoint executável
RUN chmod +x entrypoint.sh

# Usar entrypoint.sh que tem verificações robustas
CMD ["./entrypoint.sh"]
