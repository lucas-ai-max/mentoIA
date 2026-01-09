"""
Servidor API Minimalista - Versão de Emergência
Apenas rotas básicas mockadas para fazer funcionar
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Log de inicialização
print("[MAIN] Iniciando servidor minimalista...", flush=True)
print(f"[MAIN] PORT={os.getenv('PORT', '8080')}", flush=True)

app = FastAPI(title="MentorIA API - Minimal")
print("[MAIN] FastAPI app criado", flush=True)

# CORS - aceitar tudo temporariamente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TEMPORÁRIO - aceitar tudo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    print("[MAIN] GET / chamado", flush=True)
    return {"status": "ok", "service": "MentorIA API", "version": "minimal"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/admin/stats")
def stats():
    return {
        "total_agents": 0,
        "total_conversations": 0,
        "total_users": 0,
        "total_debates": 0,
        "agents_this_month": 0,
        "debates_this_week": 0,
        "llms_configured": [],
        "api_usage_percent": 0,
        "recent_activities": []
    }

@app.get("/api/admin/agents")
def agents():
    return {"agents": [], "total": 0}

@app.get("/api/admin/llms")
def llms():
    return {
        "providers": [
            {
                "provider": "openai",
                "name": "OpenAI",
                "description": "GPT Models",
                "status": "disconnected",
                "api_key": None,
                "models": {}
            },
            {
                "provider": "anthropic",
                "name": "Anthropic",
                "description": "Claude Models",
                "status": "disconnected",
                "api_key": None,
                "models": {}
            },
            {
                "provider": "google",
                "name": "Google",
                "description": "Gemini Models",
                "status": "disconnected",
                "api_key": None,
                "models": {}
            }
        ]
    }

@app.get("/api/admin/settings")
def settings():
    return {
        "settings": {
            "debate_config": {},
            "api_limits": {},
            "security": {}
        }
    }

@app.post("/api/admin/agents")
def create_agent():
    return {"id": "temp-123", "message": "ok", "status": "created"}

@app.get("/api/agents")
def get_agents():
    return {"agents": []}

@app.get("/api/debug/runtime")
def debug_runtime():
    return {
        "status": "ok",
        "app_routes_count": len(app.routes),
        "version": "minimal",
        "message": "Servidor minimalista funcionando"
    }
