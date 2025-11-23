#!/bin/bash
set -e

echo "=========================================="
echo "Starting API server..."
echo "PORT=${PORT:-8080}"
echo "HOST=0.0.0.0"
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"
echo "=========================================="

# Testar se o módulo pode ser importado
echo "Testing module import..."
python -c "import api_server; print('Module imported successfully')" || {
    echo "ERROR: Failed to import api_server module"
    exit 1
}

echo "Starting uvicorn server..."
# Executar uvicorn com tratamento de erro
exec uvicorn api_server:app \
    --host 0.0.0.0 \
    --port ${PORT:-8080} \
    --workers 1 \
    --log-level info \
    --timeout-keep-alive 600 \
    --access-log

