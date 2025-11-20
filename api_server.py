"""
Servidor API Python para integração com a interface web Next.js
Execute: python api_server.py
"""
import sys
import io

# Configurar encoding UTF-8 para stdout/stderr (resolve problema com emojis no Windows)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from agents import AGENTES_DISPONIVEIS
from debate_crew import DebateCrew
from database import Database
import uvicorn

# Importar router de admin com tratamento de erro
admin_router = None
try:
    from api_admin import router as admin_router
    print("[API_SERVER] Router de admin importado com sucesso")
    print(f"[API_SERVER] Router prefix: {admin_router.prefix if admin_router else 'None'}")
    print(f"[API_SERVER] Numero de rotas no router: {len(admin_router.routes) if admin_router else 0}")
except Exception as e:
    print(f"[API_SERVER] ERRO ao importar router de admin: {str(e)}")
    import traceback
    traceback.print_exc()

app = FastAPI(title="BillIA API")

# Verificar se admin_router foi importado
print(f"[API_SERVER] admin_router apos importacao: {admin_router}")
print(f"[API_SERVER] Tipo de admin_router: {type(admin_router)}")

# Inicializar banco de dados
# IMPORTANTE: Usar a mesma instância do Database que está em api_admin.py
# para garantir consistência
db = Database()
print(f"[API_SERVER] Database inicializado: {db}")

# Testar conexão na inicialização
try:
    print("[API_SERVER] Iniciando servidor...")
    if db.test_connection():
        print("[API_SERVER] Conexao com Supabase OK")
        if db.check_tables_exist():
            print("[API_SERVER] Tabelas verificadas")
        else:
            print("[API_SERVER] AVISO: Tabelas podem nao existir. Execute supabase_schema.sql no Supabase")
    else:
        print("[API_SERVER] Aviso: Problemas na conexao com o banco de dados")
except Exception as e:
    print(f"[API_SERVER] Erro ao testar conexao: {str(e)}")
    import traceback
    traceback.print_exc()

# CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar router de admin ANTES das outras rotas
if admin_router:
    app.include_router(admin_router)
    print("[API_SERVER] Rotas de admin registradas: /api/admin/*")
    # Listar todas as rotas registradas para debug
    print(f"[API_SERVER] Total de rotas registradas: {len(app.routes)}")
    admin_routes = [r.path for r in app.routes if hasattr(r, 'path') and '/api/admin' in r.path]
    print(f"[API_SERVER] Rotas de admin encontradas: {len(admin_routes)}")
    if admin_routes:
        print(f"[API_SERVER] Exemplos: {admin_routes[:3]}")
else:
    print("[API_SERVER] AVISO: Router de admin nao foi registrado")

class DebateRequest(BaseModel):
    agentes: List[str]
    pergunta: str
    num_rodadas: int

@app.get("/api/agents")
async def get_agents():
    """Retorna lista de agentes disponíveis do banco de dados"""
    try:
        # Buscar agentes do banco de dados
        result = db.supabase.table("agents").select("*").execute()
        
        if result.data and len(result.data) > 0:
            agents = []
            for agent in result.data:
                # Filtrar apenas agentes ativos
                if agent.get("status", "active") == "active":
                    agents.append({
                        "id": str(agent["id"]),  # Usar UUID como ID
                        "name": agent["name"],
                        "role": agent["role"],
                        "avatar": agent.get("avatar", "👤"),
                        "color": agent.get("color", "#8b5cf6"),
                        "backstory": agent.get("description", agent.get("backstory", ""))
                    })
            return {"agentes": agents}
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
        print(f"[DEBATE] Iniciando debate - Agentes: {request.agentes}, Pergunta: {request.pergunta[:50]}..., Rodadas: {request.num_rodadas}")
        # Validar agentes
        if len(request.agentes) < 2:
            raise HTTPException(
                status_code=400,
                detail="Selecione pelo menos 2 agentes"
            )
        
        # Buscar agentes do banco de dados usando os IDs (UUIDs)
        nomes_agentes = []
        agentes_data = []
        usar_fallback = False
        
        try:
            # Buscar todos os agentes selecionados do banco
            for agente_id in request.agentes:
                result = db.supabase.table("agents").select("*").eq("id", agente_id).eq("status", "active").execute()
                if result.data and len(result.data) > 0:
                    agent_data = result.data[0]
                    agentes_data.append(agent_data)
                    # Usar o nome do agente do banco
                    nomes_agentes.append(agent_data["name"])
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
            
            if len(nomes_agentes) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="Selecione pelo menos 2 agentes válidos"
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
            
            if len(nomes_agentes) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="Agentes inválidos"
                )
        
        # Criar agentes CrewAI - suporta agentes dinâmicos do banco
        # Esta seção é executada após o try-except, independente de ter entrado no except ou não
        from agents import criar_agente_dinamico, obter_agente, AGENTES_DISPONIVEIS
        from rag_manager import RAGManager
        
        agentes_crewai = []
        rag_managers = {}  # Dicionário para mapear agent_id -> RAGManager
        agent_ids_map = {}  # Mapear índice do agente -> agent_id
        
        try:
            for i, nome in enumerate(nomes_agentes):
                try:
                    if usar_fallback or nome in AGENTES_DISPONIVEIS:
                        # Usar agente hardcoded se existir ou se estiver usando fallback
                        agentes_crewai.append(obter_agente(nome))
                        # Agentes hardcoded não têm RAG
                    elif i < len(agentes_data):
                        # Usar agente dinâmico do banco com RAG habilitado
                        agent_data = agentes_data[i]
                        agent_id = str(agent_data.get("id", ""))
                        agentes_crewai.append(criar_agente_dinamico(agent_data, use_rag=True, database=db))
                        
                        # Criar RAG manager separadamente e mapear por índice
                        if agent_id:
                            rag_managers[i] = RAGManager(agent_id, database=db)
                            agent_ids_map[i] = agent_id
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
            print(f"[DEBATE] Criando debate com {len(agentes_crewai)} agentes")
            debate = DebateCrew(agentes_crewai=agentes_crewai, pergunta=request.pergunta, rag_managers=rag_managers)
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
        
        for item in historico:
            print(f"[DEBATE] Processando item: tipo={item.get('tipo')}, agente={item.get('agente')}")
            if item["tipo"] == "sintese_conteudo":
                sintese_final = item["conteudo"]
                print(f"[DEBATE] Sintese encontrada: {len(sintese_final)} caracteres")
                print(f"[DEBATE] Primeiros 200 caracteres: {sintese_final[:200]}...")
            else:
                historico_formatado.append({
                    "tipo": item["tipo"],
                    "conteudo": item["conteudo"],
                    "agente": item.get("agente"),
                    "rodada": item.get("rodada")
                })
        
        print(f"[DEBATE] Historico formatado: {len(historico_formatado)} itens")
        print(f"[DEBATE] Sintese final: {'Sim' if sintese_final else 'Nao'}")
        if sintese_final:
            print(f"[DEBATE] Tamanho da sintese: {len(sintese_final)} caracteres")
        
        # Salvar debate no banco de dados
        debate_id = None
        try:
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
            # Ainda retorna a resposta, mas loga o erro claramente
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
        debates = db.list_debates(limit)
        return {"debates": debates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar debates: {str(e)}")

@app.delete("/api/debate/{debate_id}")
async def delete_debate(debate_id: str):
    """Deleta um debate"""
    try:
        success = db.delete_debate(debate_id)
        if not success:
            raise HTTPException(status_code=500, detail="Erro ao deletar debate")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar debate: {str(e)}")

@app.get("/api/health")
async def health():
    """Health check"""
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
        folders = db.list_folders()
        return {"folders": folders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar pastas: {str(e)}")

@app.put("/api/folders/{folder_id}")
async def update_folder(folder_id: str, folder: FolderUpdate):
    """Atualiza uma pasta"""
    try:
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
    uvicorn.run(app, host="0.0.0.0", port=8000)

