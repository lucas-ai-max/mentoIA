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
port = int(os.getenv("PORT", "8080"))
print(f"PORT={port}", flush=True)
print("=" * 50, flush=True)

try:
    # Importar uvicorn primeiro
    import uvicorn
    print("[START] uvicorn importado", flush=True)
    
    # Importar app (pode demorar devido ao CrewAI)
    print("[START] Importando api_server...", flush=True)
    from api_server import app
    print("[START] api_server importado com sucesso", flush=True)
    
    host = "0.0.0.0"
    
    print(f"[START] Iniciando uvicorn em {host}:{port}...", flush=True)
    print(f"[START] Servidor pronto para receber requisições", flush=True)
    
    # Usar uvicorn.run com configurações otimizadas
    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=1,
        log_level="info",
        access_log=True,
        timeout_keep_alive=600
    )
except KeyboardInterrupt:
    print("[START] Servidor interrompido pelo usuário", flush=True)
    sys.exit(0)
except Exception as e:
    print(f"[START] ERRO CRÍTICO ao iniciar servidor: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

