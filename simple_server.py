"""
Servidor simplificado para Cloud Run - COM conexão ao banco (lazy loading)
"""
import os
from fastapi import FastAPI, HTTPException
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

# Conexão com Supabase (lazy loading)
_supabase_client = None

def get_supabase():
    """Inicializa conexão com Supabase apenas quando necessário"""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client
    
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            print("[SIMPLE_SERVER] AVISO: Credenciais do Supabase não configuradas")
            return None
        
        _supabase_client = create_client(url, key)
        print("[SIMPLE_SERVER] Conexão com Supabase estabelecida")
        return _supabase_client
    except Exception as e:
        print(f"[SIMPLE_SERVER] Erro ao conectar Supabase: {e}")
        return None

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

# Rota de agentes - conecta ao Supabase
@app.get("/api/agents")
def get_agents():
    """Retorna agentes do banco de dados"""
    try:
        supabase = get_supabase()
        if not supabase:
            return {"agentes": []}
        
        result = supabase.table("agents").select("*").eq("status", "active").execute()
        
        if result.data and len(result.data) > 0:
            agents = []
            for agent in result.data:
                agents.append({
                    "id": str(agent["id"]),
                    "name": agent["name"],
                    "role": agent["role"],
                    "avatar": agent.get("avatar", "👤"),
                    "color": agent.get("color", "#8b5cf6"),
                    "backstory": agent.get("description", agent.get("backstory", ""))
                })
            return {"agentes": agents}
        return {"agentes": []}
    except Exception as e:
        print(f"[SIMPLE_SERVER] Erro ao buscar agentes: {e}")
        return {"agentes": []}

# Rotas de admin - conectam ao Supabase
@app.get("/api/admin/agents")
def admin_list_agents(search: str = None, llm: str = None, status: str = None):
    """Lista de agentes para admin"""
    try:
        supabase = get_supabase()
        if not supabase:
            return {"agents": []}
        
        query = supabase.table("agents").select("*")
        
        if status:
            query = query.eq("status", status)
        if llm:
            query = query.eq("llm_model", llm)
        
        result = query.order("created_at", desc=True).execute()
        agents = result.data if result.data else []
        
        if search:
            search_lower = search.lower()
            agents = [
                agent for agent in agents
                if search_lower in agent.get("name", "").lower()
                or search_lower in agent.get("role", "").lower()
            ]
        
        return {"agents": agents}
    except Exception as e:
        print(f"[SIMPLE_SERVER] Erro ao listar agentes admin: {e}")
        return {"agents": []}

@app.get("/api/admin/stats")
def admin_stats():
    """Estatísticas do dashboard"""
    try:
        from datetime import datetime, timedelta
        supabase = get_supabase()
        if not supabase:
            return {
                "total_agents": 0,
                "agents_this_month": 0,
                "total_debates": 0,
                "debates_this_week": 0,
                "llms_count": 0,
                "llms_list": ["Nenhum configurado"],
                "api_usage_percent": 0,
                "recent_activities": []
            }
        
        # Total de agentes ativos
        agents_result = supabase.table("agents").select("id").eq("status", "active").execute()
        total_agents = len(agents_result.data) if agents_result.data else 0
        
        # Agentes criados este mês
        now = datetime.now()
        first_day_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        agents_this_month_result = supabase.table("agents").select("id").eq("status", "active").gte("created_at", first_day_month.isoformat()).execute()
        agents_this_month = len(agents_this_month_result.data) if agents_this_month_result.data else 0
        
        # Total de debates
        debates_result = supabase.table("debates").select("id").execute()
        total_debates = len(debates_result.data) if debates_result.data else 0
        
        # Debates esta semana
        first_day_week = now - timedelta(days=now.weekday())
        first_day_week = first_day_week.replace(hour=0, minute=0, second=0, microsecond=0)
        debates_this_week_result = supabase.table("debates").select("id").gte("created_at", first_day_week.isoformat()).execute()
        debates_this_week = len(debates_this_week_result.data) if debates_this_week_result.data else 0
        
        # LLMs configurados
        llms_result = supabase.table("llm_providers").select("provider, config, status").eq("status", "connected").execute()
        llms_count = len(llms_result.data) if llms_result.data else 0
        
        return {
            "total_agents": total_agents,
            "agents_this_month": agents_this_month,
            "total_debates": total_debates,
            "debates_this_week": debates_this_week,
            "llms_count": llms_count,
            "llms_list": ["OpenAI", "Anthropic"] if llms_count > 0 else ["Nenhum configurado"],
            "api_usage_percent": 0,
            "recent_activities": []
        }
    except Exception as e:
        print(f"[SIMPLE_SERVER] Erro ao buscar stats: {e}")
        return {
            "total_agents": 0,
            "agents_this_month": 0,
            "total_debates": 0,
            "debates_this_week": 0,
            "llms_count": 0,
            "llms_list": ["Nenhum configurado"],
            "api_usage_percent": 0,
            "recent_activities": []
        }

# Inicialização se executado diretamente
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
