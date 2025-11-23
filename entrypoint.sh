#!/bin/bash
set -e

echo "Starting API server..."
echo "PORT=${PORT:-8080}"
echo "HOST=0.0.0.0"

# Executar uvicorn com tratamento de erro
exec uvicorn api_server:app \
    --host 0.0.0.0 \
    --port ${PORT:-8080} \
    --workers 1 \
    --log-level info \
    --timeout-keep-alive 600

