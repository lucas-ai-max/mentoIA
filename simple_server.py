"""
Servidor simplificado para Cloud Run - SEM imports pesados
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MentoIA API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://web-rust-pi-54.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health checks
@app.get("/")
def root():
    return {"status": "ok", "message": "MentoIA API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/health")
def api_health():
    return {"status": "ok", "service": "mentoia-api"}

# Rota de agentes - retorna vazio por enquanto
@app.get("/api/agents")
def get_agents():
    """Retorna lista vazia - Database será conectado depois"""
    return {"agentes": []}

# Inicialização se executado diretamente
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
