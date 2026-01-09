FROM python:3.11-slim

# Configurar Python para não segurar logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Instalar apenas fastapi e uvicorn (minimalista)
RUN pip install --no-cache-dir fastapi uvicorn

# Copiar apenas main.py (minimalista)
COPY main.py .

# Expor porta
EXPOSE 8080

# Usar main.py minimalista - PORT é definido automaticamente pelo Cloud Run
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1
