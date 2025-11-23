#!/usr/bin/env python3
"""
Wrapper seguro para iniciar o servidor FastAPI
Garante que o servidor sempre inicia, mesmo com erros de import
"""
import os
import sys

# Definir variáveis de ambiente ANTES de qualquer import
os.environ.setdefault("CREWAI_TELEMETRY_OPT_OUT", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")

# Forçar flush imediato
sys.stdout.flush()
sys.stderr.flush()

print("=" * 50, flush=True)
print("Iniciando servidor FastAPI...", flush=True)
print(f"PORT={os.getenv('PORT', '8080')}", flush=True)
print("=" * 50, flush=True)

try:
    # Importar e iniciar o servidor
    import uvicorn
    from api_server import app
    
    port = int(os.getenv("PORT", "8080"))
    host = "0.0.0.0"
    
    print(f"Iniciando uvicorn em {host}:{port}...", flush=True)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=1,
        log_level="info"
    )
except Exception as e:
    print(f"ERRO CRÍTICO ao iniciar servidor: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

