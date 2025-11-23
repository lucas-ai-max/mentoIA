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

# Verificar se uvicorn está instalado
echo "Checking uvicorn installation..."
python -c "import uvicorn; print(f'uvicorn version: {uvicorn.__version__}')" || {
    echo "ERROR: uvicorn not found. Installing..."
    pip install uvicorn
}

# Verificar se o módulo pode ser importado
echo "Testing module import..."
python -c "import api_server; print('Module imported successfully')" || {
    echo "ERROR: Failed to import api_server module"
    exit 1
}

echo "Starting uvicorn server on ${HOST}:${PORT}..."

# Executar uvicorn - usar exec para substituir o processo shell
exec python -m uvicorn api_server:app \
    --host "${HOST}" \
    --port "${PORT}" \
    --workers 1 \
    --log-level info \
    --timeout-keep-alive 600 \
    --access-log \
    --no-use-colors

