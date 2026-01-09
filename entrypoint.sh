#!/bin/bash
set -euo pipefail

PORT=${PORT:-8080}
HOST="0.0.0.0"

echo "=========================================="
echo "Starting API server..."
echo "PORT=${PORT}"
echo "HOST=${HOST}"
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"
echo "=========================================="

# NÃO testar import antes, pois pode travar
# Deixar o uvicorn lidar com erros de import

echo "Starting uvicorn server on ${HOST}:${PORT}..."

# Executar uvicorn - usar exec para substituir o processo shell
exec python -m uvicorn api_server:app \
    --host "${HOST}" \
    --port "${PORT}" \
    --workers 1 \
    --log-level info \
    --timeout-keep-alive 600 \
    --access-log

