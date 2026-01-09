"""
Servidor API Python para integração com a interface web Next.js
Execute: python api_server.py
"""
import sys
import os

# ⚠️ CRÍTICO: Definir variáveis de ambiente ANTES de qualquer import do CrewAI
# Isso evita que o CrewAI tente fazer prompts interativos
os.environ.setdefault("CREWAI_TELEMETRY_OPT_OUT", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
# Desabilitar fallback do LiteLLM para evitar erros quando LLM não está disponível
os.environ.setdefault("CREWAI_DISABLE_LITELLM_FALLBACK", "true")

# Adicionar logs de inicialização imediatamente
print("[API_SERVER] Variáveis de ambiente configuradas", flush=True)
print("[API_SERVER] CREWAI_TELEMETRY_OPT_OUT=" + os.getenv("CREWAI_TELEMETRY_OPT_OUT", "não definido"), flush=True)
print("[API_SERVER] OTEL_SDK_DISABLED=" + os.getenv("OTEL_SDK_DISABLED", "não definido"), flush=True)
print("[API_SERVER] Iniciando importações...", flush=True)

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from typing import List, Dict, Optional
    print("[API_SERVER] FastAPI importado com sucesso", flush=True)
except Exception as e:
    print(f"[API_SERVER] ERRO ao importar FastAPI: {str(e)}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

# LAZY IMPORTS - Não importar CrewAI no nível do módulo para acelerar startup
# Essas importações pesadas serão feitas apenas quando necessário (dentro das funções)
AGENTES_DISPONIVEIS = {}
DebateCrew = None
Database = None

print("[API_SERVER] Importações pesadas (CrewAI) serão feitas lazy (quando necessário)", flush=True)

import uvicorn
print("[API_SERVER] Uvicorn importado com sucesso", flush=True)

# NÃO importar admin_router aqui - será feito lazy no startup
admin_router = None

app = FastAPI(title="BillIA API")
print("[API_SERVER] FastAPI app criado com sucesso", flush=True)

# Importar admin router ANTES do startup event (mas de forma segura)
try:
    # #region debug log
    import json
    try:
        with open('.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"id": "log_init_import_start", "timestamp": int(__import__('time').time() * 1000), "location": "api_server.py:54", "message": "Iniciando importação de api_admin", "data": {}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "A"}) + "\n")
    except: pass
    # #endregion
    print("[API_SERVER] Importando api_admin...", flush=True)
    from api_admin import router as admin_router_imported
    # #region debug log
    try:
        with open('.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"id": "log_init_import_success", "timestamp": int(__import__('time').time() * 1000), "location": "api_server.py:60", "message": "api_admin importado com sucesso", "data": {"prefix": admin_router_imported.prefix, "routes_count": len(admin_router_imported.routes)}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "A"}) + "\n")
    except: pass
    # #endregion
    print(f"[API_SERVER] Router importado: prefix={admin_router_imported.prefix}", flush=True)
    print(f"[API_SERVER] Total de rotas no router: {len(admin_router_imported.routes)}", flush=True)
    
    # Listar todas as rotas antes de registrar
    print("[API_SERVER] Rotas no router antes de registrar:", flush=True)
    for route in admin_router_imported.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = list(route.methods) if route.methods else []
            print(f"  {route.path} {methods}", flush=True)
    
    # #region debug log
    try:
        with open('.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"id": "log_before_include_router", "timestamp": int(__import__('time').time() * 1000), "location": "api_server.py:77", "message": "Antes de include_router", "data": {"routes_count": len(admin_router_imported.routes)}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "C"}) + "\n")
    except: pass
    # #endregion
    app.include_router(admin_router_imported)
    # #region debug log
    try:
        with open('.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"id": "log_after_include_router", "timestamp": int(__import__('time').time() * 1000), "location": "api_server.py:79", "message": "Após include_router", "data": {"app_routes_count": len(app.routes)}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "C"}) + "\n")
    except: pass
    # #endregion
    print("[API_SERVER] Router de admin registrado com sucesso", flush=True)
    
    # Listar rotas registradas no app para debug
    print("[API_SERVER] Rotas registradas no app após include_router:", flush=True)
    admin_routes_in_app = []
    for route in app.routes:
        if hasattr(route, 'path') and '/api/admin' in route.path:
            methods = list(route.methods) if hasattr(route, 'methods') and route.methods else []
            admin_routes_in_app.append(f"{route.path} {methods}")
            print(f"  {route.path} {methods}", flush=True)
    
    print(f"[API_SERVER] Total de rotas de admin no app: {len(admin_routes_in_app)}", flush=True)
    
    # Verificar especificamente as rotas problemáticas
    llms_routes = [r for r in admin_routes_in_app if '/llms' in r]
    agents_post_routes = [r for r in admin_routes_in_app if '/agents' in r and 'POST' in r]
    print(f"[API_SERVER] Rotas /llms encontradas: {llms_routes}", flush=True)
    print(f"[API_SERVER] Rotas POST /agents encontradas: {agents_post_routes}", flush=True)
    
except Exception as e:
    # #region debug log
    import json, traceback
    try:
        with open('.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"id": "log_init_import_error", "timestamp": int(__import__('time').time() * 1000), "location": "api_server.py:104", "message": "ERRO ao importar api_admin", "data": {"error": str(e), "error_type": type(e).__name__, "traceback": traceback.format_exc()[:500]}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "A"}) + "\n")
    except: pass
    # #endregion
    print(f"[API_SERVER] ERRO ao importar api_admin: {str(e)}", flush=True)
    import traceback
    traceback.print_exc()
    print("[API_SERVER] Continuando sem rotas de admin", flush=True)

# Inicializar banco de dados - LAZY LOADING para acelerar startup
db = None

def get_database():
    """Lazy initialization do Database - só carrega quando necessário"""
    global db, Database
    if db is not None:
        return db
    
    try:
        if Database is None:
            print("[API_SERVER] Importando Database (lazy)...", flush=True)
            from database import Database as DatabaseClass
            Database = DatabaseClass
        
        print("[API_SERVER] Inicializando Database (lazy)...", flush=True)
        db = Database()
        print("[API_SERVER] Database inicializado com sucesso", flush=True)
        return db
    except Exception as e:
        print(f"[API_SERVER] ERRO ao inicializar Database: {str(e)}", flush=True)
        return None

# Evento de startup - inicializar Database após o servidor iniciar
@app.on_event("startup")
async def startup_event():
    """Startup event - não fazer nada pesado aqui"""
    # #region debug log
    import json
    try:
        with open('.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"id": "log_startup_event", "timestamp": int(__import__('time').time() * 1000), "location": "api_server.py:120", "message": "Startup event executado", "data": {"app_routes_count": len(app.routes)}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "E"}) + "\n")
    except: pass
    # #endregion
    print("[API_SERVER] Startup event: Servidor pronto!", flush=True)
    print("[API_SERVER] Rotas de admin e database serão carregados lazy", flush=True)
    
    print("[API_SERVER] Startup event: Servidor pronto!", flush=True)
    print("[API_SERVER] Database será inicializado na primeira requisição (lazy)", flush=True)

# CORS para permitir requisições do frontend
# Obter origens permitidas das variáveis de ambiente
# Default inclui localhost e o domínio Vercel de produção
DEFAULT_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000,https://web-rust-pi-54.vercel.app"
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", DEFAULT_ORIGINS)
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",") if origin.strip()]

print(f"[API_SERVER] CORS configurado para origens: {ALLOWED_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("[API_SERVER] CORS middleware configurado", flush=True)

# Middleware de logging para capturar todas as requisições e erros
try:
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request as StarletteRequest
    import time

    class LoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: StarletteRequest, call_next):
            try:
                start_time = time.time()
                path = request.url.path
                method = request.method
                
                print(f"[MIDDLEWARE] {method} {path} - Início", flush=True)
                
                try:
                    response = await call_next(request)
                    process_time = time.time() - start_time
                    print(f"[MIDDLEWARE] {method} {path} - Status: {response.status_code} - Tempo: {process_time:.3f}s", flush=True)
                    return response
                except Exception as e:
                    process_time = time.time() - start_time
                    import traceback
                    error_traceback = traceback.format_exc()
                    print(f"[MIDDLEWARE] {method} {path} - ERRO após {process_time:.3f}s: {str(e)}", flush=True)
                    print(f"[MIDDLEWARE] Traceback: {error_traceback}", flush=True)
                    raise
            except Exception as middleware_error:
                # Se o middleware falhar, tentar processar sem ele
                print(f"[MIDDLEWARE] ERRO no middleware: {str(middleware_error)}", flush=True)
                return await call_next(request)

    app.add_middleware(LoggingMiddleware)
    print("[API_SERVER] Logging middleware configurado", flush=True)
except Exception as middleware_init_error:
    print(f"[API_SERVER] AVISO: Não foi possível configurar logging middleware: {str(middleware_init_error)}", flush=True)
    print("[API_SERVER] Continuando sem middleware de logging", flush=True)

# Adicionar exception handler global para capturar erros não tratados
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para capturar exceções não tratadas (exceto HTTPException)"""
    # Não capturar HTTPException - deixar o FastAPI lidar com isso
    from fastapi import HTTPException as FastAPIHTTPException
    if isinstance(exc, FastAPIHTTPException):
        raise exc
    
    import traceback
    error_traceback = traceback.format_exc()
    print(f"[API_SERVER] ERRO GLOBAL capturado em {request.url.path}: {str(exc)}", flush=True)
    print(f"[API_SERVER] Traceback: {error_traceback}", flush=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Erro interno do servidor: {str(exc)}",
            "error_type": type(exc).__name__,
            "path": str(request.url.path),
            "method": request.method,
            "traceback": error_traceback[:1000]  # Limitar tamanho
        }
    )

# NÃO registrar router de admin aqui - será feito no startup event (lazy)
print("[API_SERVER] Router de admin será registrado no startup event (lazy)", flush=True)

print("[API_SERVER] ==========================================", flush=True)
print("[API_SERVER] Módulo api_server carregado com sucesso!", flush=True)
print("[API_SERVER] App FastAPI pronto para iniciar", flush=True)
print("[API_SERVER] ==========================================", flush=True)

@app.get("/")
async def root():
    """Health check básico"""
    return {"status": "ok", "service": "MentorIA API", "version": "1.0"}

@app.get("/health")
async def health():
    """Health check para Cloud Run"""
    return {"status": "healthy"}

@app.get("/api/debug/runtime")
async def debug_runtime():
    """Endpoint de debug para verificar estado do servidor"""
    import traceback
    debug_info = {
        "app_routes_count": len(app.routes),
        "admin_routes": [],
        "all_routes": [],
        "import_status": "unknown",
        "database_status": "unknown",
        "errors": []
    }
    
    # Listar todas as rotas
    for route in app.routes:
        route_info = {
            "path": getattr(route, 'path', 'N/A'),
            "methods": list(route.methods) if hasattr(route, 'methods') and route.methods else []
        }
        debug_info["all_routes"].append(route_info)
        
        # Verificar rotas admin
        if hasattr(route, 'path') and '/api/admin' in route.path:
            debug_info["admin_routes"].append(route_info)
    
    # Verificar importação de api_admin
    try:
        from api_admin import router
        debug_info["import_status"] = "success"
        debug_info["admin_router_routes_count"] = len(router.routes)
        debug_info["admin_router_prefix"] = router.prefix
    except Exception as e:
        debug_info["import_status"] = f"failed: {str(e)}"
        debug_info["errors"].append({
            "type": "import_error",
            "error": str(e),
            "traceback": traceback.format_exc()[:500]
        })
    
    # Verificar database
    try:
        db_test = get_database()
        if db_test:
            debug_info["database_status"] = "connected"
        else:
            debug_info["database_status"] = "not_initialized"
    except Exception as e:
        debug_info["database_status"] = f"error: {str(e)}"
        debug_info["errors"].append({
            "type": "database_error",
            "error": str(e),
            "traceback": traceback.format_exc()[:500]
        })
    
    return debug_info

class DebateRequest(BaseModel):
    agentes: List[str]
    pergunta: str
    num_rodadas: int
    contexto: Optional[List[str]] = None
    modo: Optional[str] = 'debate'
    salvar: Optional[bool] = True

@app.get("/api/agents")
async def get_agents():
    """Retorna lista de agentes disponíveis do banco de dados"""
    try:
        database = get_database()
        if not database:
            # Fallback para lista vazia se database não estiver disponível
            return {"agentes": []}
        # Buscar agentes do banco de dados
        print(f"[API] Buscando agentes no Supabase...")
        result = database.supabase.table("agents").select("*").execute()
        
        print(f"[API] Query executada. Total de registros retornados: {len(result.data) if result.data else 0}")
        
        if result.data and len(result.data) > 0:
            agents = []
            active_count = 0
            for agent in result.data:
                # Filtrar apenas agentes ativos
                agent_status = agent.get("status", "active")
                if agent_status == "active":
                    active_count += 1
                    agents.append({
                        "id": str(agent["id"]),  # Usar UUID como ID
                        "name": agent["name"],
                        "role": agent["role"],
                        "avatar": agent.get("avatar", "👤"),
                        "color": agent.get("color", "#8b5cf6"),
                        "backstory": agent.get("description", agent.get("backstory", ""))
                    })
                else:
                    print(f"[API] Agente '{agent.get('name', 'N/A')}' ignorado (status: {agent_status})")
            
            print(f"[API] Total de agentes ativos: {active_count} de {len(result.data)}")
            return {"agentes": agents}
        
        print(f"[API] Nenhum agente encontrado no banco de dados")
        return {"agentes": []}
    except Exception as e:
        # Log erro sem caracteres especiais que podem causar problemas de encoding
        try:
            print(f"[API] ERRO ao buscar agentes: {str(e)}")
        except:
            pass
        return {"agentes": []}

@app.post("/api/debate/start")
async def start_debate(request: DebateRequest):
    """Inicia um novo debate"""
    try:
        print(f"[DEBATE] Iniciando debate - Agentes recebidos do frontend: {request.agentes}")
        print(f"[DEBATE] Total de agentes recebidos: {len(request.agentes)}")
        print(f"[DEBATE] Pergunta: {request.pergunta[:50]}..., Rodadas: {request.num_rodadas}")
        # Validar agentes
        if len(request.agentes) < 1:
            raise HTTPException(
                status_code=400,
                detail="Selecione pelo menos 1 agente"
            )
        
        # Buscar agentes do banco de dados usando os IDs (UUIDs)
        nomes_agentes = []
        agentes_data = []
        usar_fallback = False
        
        try:
            if not db:
                raise HTTPException(status_code=503, detail="Database não disponível. Tente novamente em alguns instantes.")
            # Buscar todos os agentes selecionados do banco
            print(f"[DEBATE] Buscando {len(request.agentes)} agentes no banco de dados...")
            for idx, agente_id in enumerate(request.agentes):
                print(f"[DEBATE] Buscando agente {idx+1}/{len(request.agentes)}: ID={agente_id}")
                result = db.supabase.table("agents").select("*").eq("id", agente_id).eq("status", "active").execute()
                if result.data and len(result.data) > 0:
                    agent_data = result.data[0]
                    agentes_data.append(agent_data)
                    # Usar o nome do agente do banco
                    nomes_agentes.append(agent_data["name"])
                    print(f"[DEBATE] ✓ Agente encontrado: {agent_data['name']}")
                else:
                    # Fallback: tentar mapear IDs antigos (compatibilidade)
                    nome_map = {
                        'elon': 'Elon Musk',
                        'bill': 'Bill Gates',
                        'jeff': 'Jeff Bezos',
                        'mark': 'Mark Zuckerberg',
                        'tim': 'Tim Cook'
                    }
                    nome = nome_map.get(agente_id.lower())
                    if nome and nome in AGENTES_DISPONIVEIS:
                        nomes_agentes.append(nome)
                        usar_fallback = True
                    else:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Agente com ID '{agente_id}' não encontrado no banco de dados"
                        )
            
            print(f"[DEBATE] Total de agentes encontrados no banco: {len(nomes_agentes)}")
            print(f"[DEBATE] Nomes dos agentes: {nomes_agentes}")
            
            if len(nomes_agentes) < 1:
                raise HTTPException(
                    status_code=400,
                    detail="Selecione pelo menos 1 agente válido"
                )
        except HTTPException:
            raise
        except Exception as e:
            print(f"[DEBATE] Erro ao buscar agentes do banco: {str(e)}")
            import traceback
            traceback.print_exc()
            # Fallback para mapeamento antigo apenas se houver erro na query
            nome_map = {
                'elon': 'Elon Musk',
                'bill': 'Bill Gates',
                'jeff': 'Jeff Bezos',
                'mark': 'Mark Zuckerberg',
                'tim': 'Tim Cook'
            }
            nomes_agentes = []
            for agente_id in request.agentes:
                nome = nome_map.get(agente_id.lower())
                if nome and nome in AGENTES_DISPONIVEIS:
                    nomes_agentes.append(nome)
                    usar_fallback = True
            
            if len(nomes_agentes) < 1:
                raise HTTPException(
                    status_code=400,
                    detail="Selecione pelo menos 1 agente válido"
                )
        
        # Criar agentes CrewAI - suporta agentes dinâmicos do banco
        # Esta seção é executada após o try-except, independente de ter entrado no except ou não
        from agents import criar_agente_dinamico, obter_agente
        from rag_manager import RAGManager
        
        # Criar mapeamento de índice -> nome do agente para salvar no histórico
        # Isso deve ser feito ANTES de criar os agentes para garantir que temos os nomes corretos
        agentes_nomes_map = {}  # índice -> nome do agente
        for i, nome in enumerate(nomes_agentes):
            # Se temos dados do banco, usar o nome do banco; senão usar o nome do fallback
            if i < len(agentes_data):
                agent_data = agentes_data[i]
                agentes_nomes_map[i] = agent_data.get("name", nome)
            else:
                agentes_nomes_map[i] = nome
        
        agentes_crewai = []
        rag_managers = {}  # Dicionário para mapear agent_id -> RAGManager
        agent_ids_map = {}  # Mapear índice do agente -> agent_id
        
        try:
            for i, nome in enumerate(nomes_agentes):
                try:
                    # PRIORIDADE 1: Se temos dados do banco, SEMPRE usar agente dinâmico
                    if i < len(agentes_data):
                        # Usar agente dinâmico do banco com RAG habilitado
                        agent_data = agentes_data[i]
                        agent_id = str(agent_data.get("id", ""))
                        agentes_crewai.append(criar_agente_dinamico(agent_data, use_rag=True, database=db))
                        
                        # Criar RAG manager separadamente e mapear por índice
                        if agent_id:
                            rag_managers[i] = RAGManager(agent_id, database=db)
                            agent_ids_map[i] = agent_id
                    # PRIORIDADE 2: Só usar hardcoded se NÃO tivermos dados do banco
                    elif usar_fallback or nome in AGENTES_DISPONIVEIS:
                        # Usar agente hardcoded se existir ou se estiver usando fallback
                        agentes_crewai.append(obter_agente(nome))
                        # Agentes hardcoded não têm RAG
                    else:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Agente '{nome}' não encontrado e sem dados do banco"
                        )
                except HTTPException:
                    raise
                except Exception as agent_error:
                    print(f"[DEBATE] Erro ao criar agente '{nome}': {str(agent_error)}")
                    import traceback
                    traceback.print_exc()
                    raise HTTPException(
                        status_code=500,
                        detail=f"Erro ao criar agente '{nome}': {str(agent_error)}"
                    )
        except HTTPException:
            raise
        except Exception as e:
            print(f"[DEBATE] Erro ao criar lista de agentes: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao criar agentes: {str(e)}"
            )
        
        # Validar que temos agentes criados
        if not agentes_crewai or len(agentes_crewai) == 0:
            raise HTTPException(
                status_code=500,
                detail="Nenhum agente foi criado com sucesso"
            )
        
        # Criar e executar debate com agentes já criados
        try:
            # VERIFICAÇÃO CRÍTICA
            if DebateCrew is None:
                error_msg = (
                    "DebateCrew não está disponível. "
                    "O import falhou durante a inicialização do servidor. "
                    "Verifique os logs de startup para detalhes."
                )
                print(f"[DEBATE] ERRO: {error_msg}")
                raise HTTPException(
                    status_code=503,
                    detail=error_msg
                )
            
            print(f"[DEBATE] Criando debate com {len(agentes_crewai)} agentes CrewAI")
            print(f"[DEBATE] Agentes CrewAI criados: {[agente.role for agente in agentes_crewai]}")
            print(f"[DEBATE] Mapeamento de nomes: {agentes_nomes_map}")
            modo_escolhido = request.modo or 'debate'
            debate = DebateCrew(
                agentes_crewai=agentes_crewai,
                pergunta=request.pergunta,
                rag_managers=rag_managers,
                contexto_usuario=request.contexto,
                modo=modo_escolhido,
                agentes_nomes_map=agentes_nomes_map  # Passar mapeamento de nomes
            )
            print(f"[DEBATE] Executando debate com {request.num_rodadas} rodadas")
            historico = debate.executar_debate(num_rodadas=request.num_rodadas)
            print(f"[DEBATE] Debate executado. Total de itens no histórico: {len(historico)}")
        except Exception as debate_error:
            print(f"[DEBATE] Erro ao executar debate: {str(debate_error)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao executar debate: {str(debate_error)}"
            )
        
        # Formatar resposta
        historico_formatado = []
        sintese_final = None
        
        print(f"[DEBATE] Total de itens no historico: {len(historico)}")
        print(f"[DEBATE] Tipos de itens no historico: {[item.get('tipo') for item in historico]}")
        
        summary_mode = modo_escolhido == 'sintese'
        # Obter apenas os agentes selecionados para filtrar o histórico
        agentes_selecionados_set = set(nomes_agentes)
        
        for item in historico:
            print(f"[DEBATE] Processando item: tipo={item.get('tipo')}, agente={item.get('agente')}")
            
            # Ignorar síntese e sintese_conteudo - serão processadas separadamente
            if item["tipo"] in ["sintese", "sintese_conteudo"]:
                if item["tipo"] == "sintese_conteudo" and summary_mode:
                    sintese_final = item["conteudo"]
                    print(f"[DEBATE] Sintese encontrada: {len(sintese_final)} caracteres")
                    print(f"[DEBATE] Primeiros 200 caracteres: {sintese_final[:200]}...")
                continue
            
            # Para respostas, verificar se o agente está nos selecionados
            if item["tipo"] == "resposta":
                agente_nome = item.get("agente", "")
                # Verificar se o nome do agente corresponde a algum dos selecionados
                # O agente pode vir como role (ex: "CEO da Apple") ou nome (ex: "Tim Cook")
                agente_encontrado = False
                for nome_selecionado in agentes_selecionados_set:
                    if nome_selecionado in agente_nome or agente_nome in nome_selecionado:
                        agente_encontrado = True
                        break
                
                if not agente_encontrado and agente_nome not in ["Moderador", "Sistema", "Contexto"]:
                    print(f"[DEBATE] Ignorando resposta de agente não selecionado: {agente_nome}")
                    continue
            
                historico_formatado.append({
                    "tipo": item["tipo"],
                    "conteudo": item["conteudo"],
                "agente": item.get("agente"),  # Nome do agente (prioridade)
                "agente_role": item.get("agente_role")  # Role do agente (para referência)
                })
        
        print(f"[DEBATE] Historico formatado: {len(historico_formatado)} itens")
        print(f"[DEBATE] Sintese final: {'Sim' if sintese_final else 'Nao'}")
        if sintese_final and summary_mode:
            print(f"[DEBATE] Tamanho da sintese: {len(sintese_final)} caracteres")
        
        # Salvar debate no banco de dados
        debate_id = None
        if request.salvar:
            try:
                if not db:
                    raise HTTPException(status_code=503, detail="Database não disponível. Não foi possível salvar o debate.")
                debate_id = db.save_debate(
                    pergunta=request.pergunta,
                    selected_agents=request.agentes,
                    num_rodadas=request.num_rodadas,
                    historico=historico,
                    sintese=sintese_final
                )
                print(f"[DEBATE] Debate salvo no banco com ID: {debate_id}")
            except Exception as db_error:
                print(f"[DEBATE] ERRO CRITICO ao salvar no banco: {str(db_error)}")
                print(f"[DEBATE] Tipo do erro: {type(db_error).__name__}")
                import traceback
                traceback.print_exc()
                debate_id = None
        
        return {
            "debate_id": debate_id,
            "historico": historico_formatado,
            "sintese": sintese_final
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Capturar qualquer erro não tratado
        error_msg = str(e)
        print(f"[DEBATE] ERRO NAO TRATADO: {error_msg}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao executar debate: {error_msg}"
        )

@app.get("/api/debate/{debate_id}")
async def get_debate(debate_id: str):
    """Recupera um debate salvo"""
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database não disponível.")
        debate = db.get_debate(debate_id)
        if not debate:
            raise HTTPException(status_code=404, detail="Debate não encontrado")
        return debate
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar debate: {str(e)}")

@app.get("/api/debates")
async def list_debates(limit: int = 50):
    """Lista debates recentes"""
    try:
        if not db:
            return {"debates": []}
        debates = db.list_debates(limit)
        return {"debates": debates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar debates: {str(e)}")

@app.delete("/api/debate/{debate_id}")
async def delete_debate(debate_id: str):
    """Deleta um debate"""
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database não disponível.")
        success = db.delete_debate(debate_id)
        if not success:
            raise HTTPException(status_code=500, detail="Erro ao deletar debate")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar debate: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint - usado pelo Cloud Run startup probe"""
    return {"status": "ok", "message": "BillIA API is running"}

@app.get("/api/health")
async def health():
    """Health check"""
    return {"status": "ok", "service": "mentoia-api"}

@app.get("/health")
async def health_simple():
    """Simple health check for Cloud Run"""
    return {"status": "ok"}

# ========== ENDPOINTS PARA PASTAS ==========

class FolderCreate(BaseModel):
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None

class FolderUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None

class MoveDebateRequest(BaseModel):
    debate_id: str
    folder_id: Optional[str] = None

@app.post("/api/folders")
async def create_folder(folder: FolderCreate):
    """Cria uma nova pasta"""
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database não disponível.")
        folder_id = db.create_folder(
            name=folder.name,
            icon=folder.icon,
            color=folder.color
        )
        return {"id": folder_id, "name": folder.name, "icon": folder.icon, "color": folder.color}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar pasta: {str(e)}")

@app.get("/api/folders")
async def list_folders():
    """Lista todas as pastas com contagem de debates"""
    try:
        if not db:
            return {"folders": []}
        folders = db.list_folders()
        return {"folders": folders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar pastas: {str(e)}")

@app.put("/api/folders/{folder_id}")
async def update_folder(folder_id: str, folder: FolderUpdate):
    """Atualiza uma pasta"""
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database não disponível.")
        success = db.update_folder(
            folder_id=folder_id,
            name=folder.name,
            icon=folder.icon,
            color=folder.color
        )
        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=500, detail="Erro ao atualizar pasta")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar pasta: {str(e)}")

@app.delete("/api/folders/{folder_id}")
async def delete_folder(folder_id: str):
    """Deleta uma pasta"""
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database não disponível.")
        success = db.delete_folder(folder_id)
        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=500, detail="Erro ao deletar pasta")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar pasta: {str(e)}")

@app.post("/api/folders/move-debate")
async def move_debate_to_folder(request: MoveDebateRequest):
    """Move um debate para uma pasta"""
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database não disponível.")
        success = db.move_debate_to_folder(
            debate_id=request.debate_id,
            folder_id=request.folder_id
        )
        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=500, detail="Erro ao mover debate")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao mover debate: {str(e)}")

if __name__ == "__main__":
    # Usar porta do ambiente (Cloud Run usa PORT, padrão 8080)
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        timeout_keep_alive=600,  # 10 minutos para manter conexão durante uploads grandes
        limit_concurrency=100,
        limit_max_requests=1000
    )
