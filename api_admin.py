"""
API de administração para gerenciar agentes e configurações
"""
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime
import hashlib
import uuid
import os
import re
import traceback

# Configurar logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("[API_ADMIN] Carregando modulo api_admin...", flush=True)

# LAZY IMPORT - Não importar Database no nível do módulo para acelerar startup
Database = None
DEFAULT_SYSTEM_SETTINGS = None

def _import_database():
    """Importa Database apenas quando necessário"""
    global Database, DEFAULT_SYSTEM_SETTINGS
    if Database is None:
        print("[API_ADMIN] Importando Database (lazy)...", flush=True)
        from database import Database as DB, DEFAULT_SYSTEM_SETTINGS as DSS
        Database = DB
        DEFAULT_SYSTEM_SETTINGS = DSS
    return Database, DEFAULT_SYSTEM_SETTINGS

# ⚠️ CRÍTICO: Router sempre deve ser criado, mesmo se Database falhar
router = APIRouter(prefix="/api/admin", tags=["admin"])
print(f"[API_ADMIN] Router criado com prefix: {router.prefix}")

# Database será inicializado lazy (só quando necessário)
# Isso garante que o router sempre seja exportado, mesmo se houver erros de conexão
_db_instance = None
_db_error = None

def get_db():
    """
    Lazy initialization do Database.
    Retorna a instância do Database ou levanta HTTPException se não disponível.
    """
    # #region debug log
    import json
    with open('.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"id": "log_get_db_entry", "timestamp": int(__import__('time').time() * 1000), "location": "api_admin.py:47", "message": "get_db() chamado", "data": {"_db_instance_exists": _db_instance is not None, "_db_error_exists": _db_error is not None}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
    # #endregion
    global _db_instance, _db_error, Database
    
    if _db_instance is not None:
        # #region debug log
        with open('.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"id": "log_get_db_cached", "timestamp": int(__import__('time').time() * 1000), "location": "api_admin.py:52", "message": "get_db() retornando instância cached", "data": {}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
        # #endregion
        return _db_instance
    
    if _db_error is not None:
        # #region debug log
        with open('.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"id": "log_get_db_previous_error", "timestamp": int(__import__('time').time() * 1000), "location": "api_admin.py:57", "message": "get_db() erro anterior detectado", "data": {"error": str(_db_error)}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
        # #endregion
        # Se já tentamos e falhou, retornar erro
        raise HTTPException(
            status_code=503,
            detail=f"Database não disponível: {str(_db_error)}"
        )
    
    # Importar Database se necessário
    # #region debug log
    with open('.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"id": "log_get_db_importing", "timestamp": int(__import__('time').time() * 1000), "location": "api_admin.py:64", "message": "get_db() importando Database", "data": {}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
    # #endregion
    DB, _ = _import_database()
    
    # Tentar inicializar pela primeira vez
    try:
        # #region debug log
        with open('.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"id": "log_get_db_initializing", "timestamp": int(__import__('time').time() * 1000), "location": "api_admin.py:70", "message": "get_db() inicializando Database", "data": {}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
        # #endregion
        _db_instance = DB()
        # #region debug log
        with open('.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"id": "log_get_db_success", "timestamp": int(__import__('time').time() * 1000), "location": "api_admin.py:72", "message": "get_db() Database inicializado com sucesso", "data": {}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
        # #endregion
        print("[API_ADMIN] Database inicializado (lazy)")
        return _db_instance
    except Exception as e:
        # #region debug log
        import traceback
        with open('.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"id": "log_get_db_error", "timestamp": int(__import__('time').time() * 1000), "location": "api_admin.py:75", "message": "get_db() ERRO ao inicializar Database", "data": {"error": str(e), "error_type": type(e).__name__, "traceback": traceback.format_exc()}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
        # #endregion
        _db_error = e
        print(f"[API_ADMIN] ERRO ao inicializar Database (lazy): {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=503,
            detail=f"Database não disponível: {str(e)}"
        )

# Classe wrapper para manter compatibilidade com código existente
class DatabaseWrapper:
    """Wrapper que permite usar db.supabase como antes, mas com lazy initialization"""
    def __getattr__(self, name):
        if name == 'supabase':
            return get_db().supabase
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

# Criar instância do wrapper para compatibilidade
db = DatabaseWrapper()

def sanitize_text_for_postgres(text: str) -> str:
    """
    Remove caracteres problemáticos que o PostgreSQL não aceita
    Especialmente caracteres nulos (\u0000) e outros caracteres de controle inválidos
    """
    if not text:
        return text
    
    # Remover caracteres nulos (\u0000 ou \x00)
    text = text.replace('\x00', '')
    text = text.replace('\u0000', '')
    
    # Remover outros caracteres de controle problemáticos
    # Manter: \n (0x0A - line feed), \r (0x0D - carriage return), \t (0x09 - tab)
    # Remover: outros caracteres de controle (0x00-0x08, 0x0B-0x0C, 0x0E-0x1F)
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', text)
    
    # Garantir que o texto seja válido UTF-8
    try:
        # Tentar codificar/decodificar para garantir validade
        text.encode('utf-8')
    except UnicodeEncodeError:
        # Se houver problemas, usar errors='replace' para substituir caracteres inválidos
        text = text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
    
    return text

# Models
class AgentCreate(BaseModel):
    name: str
    avatar: str
    color: str
    role: str
    goal: str
    backstory: str
    llm_provider: str
    llm_model: str
    temperature: float
    max_tokens: int
    verbose: bool = True
    allow_delegation: bool = False
    status: str = "active"
    tags: List[str] = []
    description: Optional[str] = None

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    color: Optional[str] = None
    role: Optional[str] = None
    goal: Optional[str] = None
    backstory: Optional[str] = None
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    verbose: Optional[bool] = None
    allow_delegation: Optional[bool] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None

class LLMProviderConfig(BaseModel):
    provider: str
    api_key: Optional[str] = None
    enabled_models: Optional[List[str]] = None

class LLMProviderUpdate(BaseModel):
    api_key: Optional[str] = None
    status: Optional[str] = None
    enabled_models: Optional[List[str]] = None

class LLMModelUpdate(BaseModel):
    enabled: bool

class DebateSettings(BaseModel):
    max_rounds: Optional[int] = Field(None, ge=1, le=10)
    response_timeout: Optional[int] = Field(None, ge=30, le=300)
    allow_without_min_agents: Optional[bool] = None

class ApiLimits(BaseModel):
    monthly_tokens: Optional[int] = Field(None, ge=1)
    alert_threshold: Optional[int] = Field(None, ge=1, le=100)

class SecuritySettings(BaseModel):
    enable_2fa: Optional[bool] = None
    log_activities: Optional[bool] = None
    admin_password: Optional[str] = Field(None, min_length=8)

class SettingsUpdateRequest(BaseModel):
    debate_config: Optional[DebateSettings] = None
    api_limits: Optional[ApiLimits] = None
    security: Optional[SecuritySettings] = None

def _hash_admin_password(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def _sanitize_settings_for_response(settings: Dict[str, Any]) -> Dict[str, Any]:
    _, DSS = _import_database()
    debate_config = settings.get("debate_config", DSS["debate_config"])
    api_limits = settings.get("api_limits", DSS["api_limits"])
    security = settings.get("security", {})
    return {
        "debate_config": debate_config,
        "api_limits": api_limits,
        "security": {
            "admin_password_set": bool(security.get("admin_password_hash")),
            "enable_2fa": security.get("enable_2fa", DSS["security"]["enable_2fa"]),
            "log_activities": security.get("log_activities", DSS["security"]["log_activities"]),
        },
    }

def _build_settings_update_payload(update: SettingsUpdateRequest) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    if update.debate_config:
        payload["debate_config"] = update.debate_config.dict(exclude_none=True)
    if update.api_limits:
        payload["api_limits"] = update.api_limits.dict(exclude_none=True)
    if update.security:
        security_payload = update.security.dict(exclude_none=True)
        password = security_payload.pop("admin_password", None)
        if password is not None:
            trimmed = password.strip()
            security_payload["admin_password_hash"] = _hash_admin_password(trimmed) if trimmed else None
        if security_payload:
            payload["security"] = security_payload
    return payload

def _build_settings_response(settings: Dict[str, Any]) -> Dict[str, Any]:
    response = {"settings": _sanitize_settings_for_response(settings)}
    try:
        db_instance = get_db()
        warning = db_instance.get_settings_warning() if db_instance else None
        if warning:
            response["warning"] = warning
    except HTTPException:
        # Se database não disponível, continuar sem warning
        pass
    return response

# Rotas de Agentes
@router.get("/agents")
async def list_agents(
    search: Optional[str] = None,
    llm: Optional[str] = None,
    status: Optional[str] = None
):
    """Lista todos os agentes com filtros opcionais"""
    try:
        logger.info(f"Listando agentes - search={search}, llm={llm}, status={status}")
        print(f"[API_ADMIN] Listando agentes - search={search}, llm={llm}, status={status}", flush=True)
        
        # Obter instância do Database (lazy initialization)
        try:
            db_instance = get_db()
        except HTTPException as http_err:
            logger.error(f"Erro HTTP ao obter database: {http_err.detail}")
            # Se database não disponível, retornar lista vazia em vez de erro
            logger.warning("Database não disponível, retornando lista vazia")
            return {"agents": []}
        except Exception as db_err:
            logger.error(f"Erro ao obter database: {str(db_err)}", exc_info=True)
            # Se database não disponível, retornar lista vazia em vez de erro
            logger.warning("Database não disponível, retornando lista vazia")
            return {"agents": []}
        
        # Verificar se a tabela existe
        try:
            # Primeiro, tentar uma query simples para verificar conexão
            logger.info("Testando conexão com Supabase...")
            print(f"[API_ADMIN] Testando conexao com Supabase...", flush=True)
            test_result = db_instance.supabase.table("agents").select("id").limit(1).execute()
            logger.info(f"Conexão OK. Teste retornou: {len(test_result.data) if test_result.data else 0} registros")
            print(f"[API_ADMIN] Conexao OK. Teste retornou: {len(test_result.data) if test_result.data else 0} registros", flush=True)
            
            # Agora fazer a query completa
            query = db_instance.supabase.table("agents").select("*")
            
            if status:
                query = query.eq("status", status)
                logger.info(f"Aplicando filtro status={status}")
            if llm:
                query = query.eq("llm_model", llm)
                logger.info(f"Aplicando filtro llm={llm}")
            
            logger.info("Executando query completa...")
            print(f"[API_ADMIN] Executando query completa...", flush=True)
            result = query.order("created_at", desc=True).execute()
            agents = result.data if result.data else []
            
            logger.info(f"Query executada com sucesso. {len(agents)} agentes encontrados")
            print(f"[API_ADMIN] Query executada com sucesso. {len(agents)} agentes encontrados", flush=True)
            
            # Log detalhado se não houver agentes
            if len(agents) == 0:
                logger.warning("Nenhum agente encontrado. Verificando possíveis causas...")
                print(f"[API_ADMIN] AVISO: Nenhum agente encontrado. Verificando possiveis causas...", flush=True)
                # Tentar sem filtros para ver se há algum agente
                try:
                    all_result = db_instance.supabase.table("agents").select("id, name, status").execute()
                    all_agents = all_result.data if all_result.data else []
                    logger.info(f"Total de agentes na tabela (sem filtros): {len(all_agents)}")
                    print(f"[API_ADMIN] Total de agentes na tabela (sem filtros): {len(all_agents)}", flush=True)
                    if all_agents:
                        logger.info("Agentes encontrados (primeiros 3):")
                        print(f"[API_ADMIN] Agentes encontrados (primeiros 3):", flush=True)
                        for agent in all_agents[:3]:
                            logger.info(f"  - {agent.get('name', 'N/A')} (status: {agent.get('status', 'N/A')}, id: {agent.get('id', 'N/A')})")
                            print(f"  - {agent.get('name', 'N/A')} (status: {agent.get('status', 'N/A')}, id: {agent.get('id', 'N/A')})", flush=True)
                except Exception as check_err:
                    logger.warning(f"Erro ao verificar agentes sem filtros: {str(check_err)}")
            
            if search:
                search_lower = search.lower()
                agents = [
                    agent for agent in agents
                    if search_lower in agent.get("name", "").lower()
                    or search_lower in agent.get("role", "").lower()
                ]
                logger.info(f"Após busca: {len(agents)} agentes")
                print(f"[API_ADMIN] Apos busca: {len(agents)} agentes", flush=True)
            
            return {"agents": agents}
        except Exception as table_error:
            # Log detalhado do erro
            error_msg = str(table_error).lower()
            logger.error(f"ERRO ao consultar tabela agents: {str(table_error)}", exc_info=True)
            print(f"[API_ADMIN] ERRO ao consultar tabela agents: {str(table_error)}", flush=True)
            traceback.print_exc()
            
            # Se a tabela não existir, retornar lista vazia
            if "relation" in error_msg and "does not exist" in error_msg:
                logger.warning("Tabela 'agents' não existe. Retornando lista vazia.")
                print("[API_ADMIN] AVISO: Tabela 'agents' nao existe. Retornando lista vazia.", flush=True)
                return {"agents": []}
            elif "permission denied" in error_msg or "row-level security" in error_msg:
                logger.error("RLS bloqueando acesso. Verifique as políticas RLS.")
                print("[API_ADMIN] ERRO: RLS bloqueando acesso. Verifique as politicas RLS.", flush=True)
                raise HTTPException(
                    status_code=503,
                    detail="Acesso negado pela política RLS. Verifique as configurações de segurança do Supabase."
                )
            else:
                # Para outros erros, retornar lista vazia em vez de quebrar
                logger.error(f"Erro desconhecido ao consultar tabela: {str(table_error)}")
                return {"agents": []}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERRO CRÍTICO ao listar agentes: {str(e)}", exc_info=True)
        print(f"[API_ADMIN] ERRO CRÍTICO ao listar agentes: {str(e)}", flush=True)
        traceback.print_exc()
        # Retornar lista vazia em vez de erro 500 para não quebrar o frontend
        logger.warning("Retornando lista vazia devido a erro")
        return {"agents": []}

@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Busca um agente específico"""
    try:
        db_instance = get_db()
        result = db_instance.supabase.table("agents").select("*").eq("id", agent_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar agente: {str(e)}")

@router.post("/agents")
async def create_agent(agent: AgentCreate):
    """Cria um novo agente"""
    try:
        logger.info(f"Criando novo agente: {agent.name}")
        print(f"[API_ADMIN] Criando novo agente: {agent.name}", flush=True)
        
        agent_data = agent.dict()
        agent_data["created_at"] = datetime.now().isoformat()
        agent_data["updated_at"] = datetime.now().isoformat()
        agent_data["total_debates"] = 0
        
        try:
            db_instance = get_db()
            result = db_instance.supabase.table("agents").insert(agent_data).execute()
            if not result.data:
                logger.error("Erro ao criar agente: resultado vazio do banco")
                raise HTTPException(status_code=500, detail="Erro ao criar agente: resultado vazio")
            logger.info(f"Agente criado com sucesso: {result.data[0].get('id')}")
            print(f"[API_ADMIN] Agente criado com sucesso: {result.data[0].get('id')}", flush=True)
            return result.data[0]
        except HTTPException:
            raise
        except Exception as db_err:
            logger.error(f"Erro ao criar agente no banco: {str(db_err)}", exc_info=True)
            print(f"[API_ADMIN] ERRO ao criar agente no banco: {str(db_err)}", flush=True)
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Erro ao criar agente: {str(db_err)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERRO CRÍTICO ao criar agente: {str(e)}", exc_info=True)
        print(f"[API_ADMIN] ERRO CRÍTICO ao criar agente: {str(e)}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao criar agente: {str(e)}")

@router.put("/agents/{agent_id}")
async def update_agent(agent_id: str, agent: AgentUpdate):
    """Atualiza um agente existente"""
    try:
        update_data = {k: v for k, v in agent.dict().items() if v is not None}
        update_data["updated_at"] = datetime.now().isoformat()
        
        result = db.supabase.table("agents").update(update_data).eq("id", agent_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar agente: {str(e)}")

@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Deleta um agente"""
    try:
        db.supabase.table("agents").delete().eq("id", agent_id).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar agente: {str(e)}")

@router.post("/upload-avatar")
async def upload_avatar(file: UploadFile = File(...)):
    """Faz upload de uma imagem para o Supabase Storage"""
    try:
        # Validar tipo de arquivo
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Apenas imagens sao permitidas")
        
        # Ler arquivo
        contents = await file.read()
        
        # Validar tamanho (max 5MB)
        if len(contents) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Imagem muito grande (max 5MB)")
        
        # Gerar nome unico para o arquivo
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        file_name = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"avatars/{file_name}"
        
        # Fazer upload para Supabase Storage
        result = db.supabase.storage.from_("agent-avatars").upload(
            file_path,
            contents,
            file_options={"content-type": file.content_type}
        )
        
        # Obter URL publica da imagem
        public_url = db.supabase.storage.from_("agent-avatars").get_public_url(file_path)
        
        # Se a URL nao comecar com http, adicionar o dominio do Supabase
        if not public_url.startswith('http'):
            supabase_url = os.getenv("SUPABASE_URL", "https://qkdhwwiohaqacojiijya.supabase.co")
            if public_url.startswith('/'):
                public_url = f"{supabase_url}{public_url}"
            else:
                public_url = f"{supabase_url}/{public_url}"
        
        print(f"[API_ADMIN] Upload realizado: {file_path} -> {public_url}")
        print(f"[API_ADMIN] URL completa: {public_url}")
        
        return {
            "url": public_url,
            "path": file_path
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API_ADMIN] Erro ao fazer upload: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao fazer upload: {str(e)}")

@router.post("/agents/{agent_id}/duplicate")
async def duplicate_agent(agent_id: str):
    """Duplica um agente existente"""
    try:
        # Buscar agente original
        result = db.supabase.table("agents").select("*").eq("id", agent_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        
        original = result.data[0]
        # Criar cópia
        copy_data = {k: v for k, v in original.items() if k not in ["id", "created_at", "updated_at"]}
        copy_data["name"] = f"{original['name']} (Cópia)"
        copy_data["created_at"] = datetime.now().isoformat()
        copy_data["updated_at"] = datetime.now().isoformat()
        copy_data["total_debates"] = 0
        
        result = db.supabase.table("agents").insert(copy_data).execute()
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao duplicar agente: {str(e)}")

class TestMessageRequest(BaseModel):
    test_message: str

@router.post("/agents/{agent_id}/test")
async def test_agent(agent_id: str, request: TestMessageRequest):
    """Testa um agente com uma mensagem"""
    try:
        # Buscar agente
        result = db.supabase.table("agents").select("*").eq("id", agent_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        
        agent_data = result.data[0]
        
        # Criar agente temporário e testar
        from agents import criar_agente_dinamico
        agent = criar_agente_dinamico(agent_data)
        
        # Executar teste (simplificado)
        # TODO: Implementar teste real com CrewAI
        return {
            "response": f"Teste do agente {agent_data['name']}: {request.test_message}",
            "agent": agent_data["name"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao testar agente: {str(e)}")

# Rotas de LLMs
@router.get("/llms")
async def list_llm_providers():
    """Lista todos os provedores de LLM com suas configurações"""
    try:
        logger.info("Listando providers LLM...")
        print("[API_ADMIN] Listando providers LLM...", flush=True)
        
        # Tentar obter database, mas não falhar se não disponível
        providers_data = []
        try:
            db_instance = get_db()
            # Buscar configurações do banco
            result = db_instance.supabase.table("llm_providers").select("*").execute()
            providers_data = result.data if result.data else []
            logger.info(f"Encontrados {len(providers_data)} providers no banco")
        except Exception as db_err:
            logger.warning(f"Erro ao buscar providers do banco: {str(db_err)}. Continuando com providers padrão.")
            print(f"[API_ADMIN] AVISO: Erro ao buscar providers do banco: {str(db_err)}. Continuando com providers padrão.", flush=True)
            providers_data = []
        
        # Criar dicionário com providers padrão
        providers_map = {
            "openai": {
                "provider": "openai",
                "name": "OpenAI",
                "description": "GPT Models",
                "status": "disconnected",
                "api_key": None,
                "models": {
                    "gpt-4": {"name": "GPT-4", "cost": "$0.03/1k tokens", "enabled": False},
                    "gpt-4-turbo": {"name": "GPT-4 Turbo", "cost": "$0.01/1k tokens", "enabled": False},
                    "gpt-4.1": {"name": "GPT-4.1", "cost": "$0.03/1k tokens", "enabled": False},
                    "gpt-4.1-mini": {"name": "GPT-4.1 Mini", "cost": "$0.015/1k tokens", "enabled": False},
                    "gpt-3.5-turbo": {"name": "GPT-3.5 Turbo", "cost": "$0.002/1k tokens", "enabled": False},
                }
            },
            "anthropic": {
                "provider": "anthropic",
                "name": "Anthropic",
                "description": "Claude Models",
                "status": "disconnected",
                "api_key": None,
                "models": {
                    "claude-sonnet-4-20250514": {"name": "Claude Sonnet 4.5", "cost": "$0.003/1k tokens", "enabled": False, "description": "Mais inteligente para tarefas do dia a dia"},
                    "claude-opus-4-20250514": {"name": "Claude Opus 4.1", "cost": "$0.015/1k tokens", "enabled": False, "description": "Modelo avançado para brainstorming. Consome uso mais rapidamente"},
                    "claude-haiku-4-20250514": {"name": "Claude Haiku 4.5", "cost": "$0.00025/1k tokens", "enabled": False, "description": "Mais rápido para respostas rápidas"},
                    "claude-3-5-sonnet-20241022": {"name": "Claude 3.5 Sonnet", "cost": "$0.003/1k tokens", "enabled": False},
                    "claude-3-opus-20240229": {"name": "Claude 3 Opus", "cost": "$0.015/1k tokens", "enabled": False},
                    "claude-3-sonnet-20240229": {"name": "Claude 3 Sonnet", "cost": "$0.003/1k tokens", "enabled": False},
                    "claude-3-haiku-20240307": {"name": "Claude 3 Haiku", "cost": "$0.00025/1k tokens", "enabled": False},
                }
            },
            "google": {
                "provider": "google",
                "name": "Google",
                "description": "Gemini Models",
                "status": "disconnected",
                "api_key": None,
                "models": {
                    "gemini-3-pro": {
                        "name": "Gemini 3 Pro",
                        "cost": "$0.00125/1k tokens",
                        "enabled": False,
                        "description": "O mais avançado. Ideal para tarefas complexas, raciocínio de ponta, análise multimodal e recursos de agente/codificação mais avançados."
                    },
                    "gemini-2.5-pro": {
                        "name": "Gemini 2.5 Pro",
                        "cost": "$0.00125/1k tokens",
                        "enabled": False,
                        "description": "Raciocínio Avançado. Excelente para problemas complexos em código, matemática, STEM, e análise de grandes documentos ou bases de dados."
                    },
                    "gemini-2.5-flash": {
                        "name": "Gemini 2.5 Flash",
                        "cost": "$0.000075/1k tokens",
                        "enabled": False,
                        "description": "Custo-Benefício e Velocidade. O modelo mais equilibrado. Ideal para alta frequência, baixa latência, processamento em larga escala e casos de uso de agentes."
                    },
                    "gemini-2.5-flash-lite": {
                        "name": "Gemini 2.5 Flash-Lite",
                        "cost": "$0.00005/1k tokens",
                        "enabled": False,
                        "description": "Mais Rápido e Econômico. Nosso modelo multimodal mais rápido e econômico, com ótimo desempenho para tarefas de alta frequência."
                    },
                }
            }
        }
        
        # Atualizar com dados do banco
        for provider_data in providers_data:
            provider_name = provider_data.get("provider", "").lower()
            if provider_name in providers_map:
                status = provider_data.get("status", "disconnected")
                providers_map[provider_name]["status"] = status
                
                if provider_data.get("api_key_encrypted"):
                    # Se estiver conectado, mostrar parte da chave
                    if status == "connected":
                        api_key_full = provider_data.get("api_key_encrypted", "")
                        if len(api_key_full) > 10:
                            # Primeiros 7 caracteres + ... + últimos 4 caracteres
                            masked_key = f"{api_key_full[:7]}...{api_key_full[-4:]}"
                        else:
                            masked_key = "***"
                        providers_map[provider_name]["api_key"] = masked_key
                    else:
                        # Se não estiver conectado, não mostrar chave
                        providers_map[provider_name]["api_key"] = None
                
                # Carregar modelos habilitados do config JSONB
                config = provider_data.get("config", {})
                if isinstance(config, dict):
                    enabled_models = config.get("enabled_models", [])
                    for model_key in providers_map[provider_name]["models"]:
                        if model_key in enabled_models:
                            providers_map[provider_name]["models"][model_key]["enabled"] = True
        
        providers_list = list(providers_map.values())
        logger.info(f"Retornando {len(providers_list)} providers")
        return {"providers": providers_list}
    except Exception as e:
        logger.error(f"ERRO ao listar LLMs: {str(e)}", exc_info=True)
        print(f"[API_ADMIN] Erro ao listar LLMs: {str(e)}", flush=True)
        traceback.print_exc()
        # Em caso de erro, retornar providers padrão em vez de quebrar
        logger.warning("Retornando providers padrão devido a erro")
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

@router.get("/llms/{provider}")
async def get_llm_provider(provider: str):
    """Obtém configuração de um provedor específico"""
    try:
        result = db.supabase.table("llm_providers").select("*").eq("provider", provider.lower()).execute()
        if result.data and len(result.data) > 0:
            provider_data = result.data[0]
            return {
                "provider": provider_data.get("provider"),
                "status": provider_data.get("status", "disconnected"),
                "api_key": "***" if provider_data.get("api_key_encrypted") else None,
                "config": provider_data.get("config", {}),
                "created_at": provider_data.get("created_at"),
                "updated_at": provider_data.get("updated_at")
            }
        else:
            return {
                "provider": provider.lower(),
                "status": "disconnected",
                "api_key": None,
                "config": {},
                "created_at": None,
                "updated_at": None
            }
    except Exception as e:
        print(f"[API_ADMIN] Erro ao buscar LLM {provider}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar provedor: {str(e)}")

@router.put("/llms/{provider}")
async def update_llm_provider(provider: str, config: LLMProviderUpdate):
    """Salva ou atualiza configuração de um provedor"""
    try:
        provider_lower = provider.lower()
        
        # Verificar se já existe
        existing = db.supabase.table("llm_providers").select("*").eq("provider", provider_lower).execute()
        
        update_data = {
            "provider": provider_lower,
            "updated_at": datetime.now().isoformat()
        }
        
        if config.api_key is not None:
            # Se api_key for string vazia, deletar a chave
            if config.api_key == "":
                update_data["api_key_encrypted"] = None
                update_data["status"] = "disconnected"
            else:
                # Armazenar API key (em produção, criptografar)
                update_data["api_key_encrypted"] = config.api_key
                # Se status foi fornecido explicitamente, usar ele; caso contrário, desconectar ao salvar nova chave
                if config.status:
                    update_data["status"] = config.status
                else:
                    # Ao salvar nova chave, sempre desconectar até testar novamente
                    update_data["status"] = "disconnected"
        
        # Se status foi fornecido explicitamente (mesmo sem api_key), usar ele
        if config.status and "status" not in update_data:
            update_data["status"] = config.status
        
        if config.enabled_models is not None:
            # Buscar config atual ou criar novo
            current_config = {}
            if existing.data and len(existing.data) > 0:
                current_config = existing.data[0].get("config", {}) or {}
            
            current_config["enabled_models"] = config.enabled_models
            update_data["config"] = current_config
        
        if existing.data and len(existing.data) > 0:
            # Atualizar existente
            result = db.supabase.table("llm_providers").update(update_data).eq("provider", provider_lower).execute()
        else:
            # Criar novo
            update_data["created_at"] = datetime.now().isoformat()
            result = db.supabase.table("llm_providers").insert(update_data).execute()
        
        return {"success": True, "provider": provider_lower}
    except Exception as e:
        print(f"[API_ADMIN] Erro ao atualizar LLM {provider}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar provedor: {str(e)}")

@router.post("/llms/{provider}/test")
async def test_llm_connection(provider: str):
    """Testa conexão com um provedor"""
    try:
        # Buscar API key do banco
        result = db.supabase.table("llm_providers").select("*").eq("provider", provider.lower()).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Provedor não configurado")
        
        provider_data = result.data[0]
        api_key = provider_data.get("api_key_encrypted")
        
        if not api_key:
            raise HTTPException(status_code=400, detail="API key não configurada")
        
        # Testar conexão baseado no provider
        provider_lower = provider.lower()
        
        connected = False
        if provider_lower == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            # Fazer chamada simples para testar
            response = client.models.list()
            connected = True
        
        elif provider_lower == "anthropic":
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            # Listar modelos para testar
            client.models.list()
            connected = True
        
        elif provider_lower == "google":
            # Google Gemini test
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            models = genai.list_models()
            connected = True
        
        else:
            raise HTTPException(status_code=400, detail=f"Provedor {provider_lower} não suportado")
        
        # Se conectou com sucesso, atualizar status no banco
        if connected:
            update_data = {
                "status": "connected",
                "updated_at": datetime.now().isoformat()
            }
            db.supabase.table("llm_providers").update(update_data).eq("provider", provider_lower).execute()
            return {"connected": True, "provider": provider_lower, "message": "Conexão testada com sucesso"}
        else:
            return {"connected": False, "provider": provider_lower, "message": "Conexão falhou"}
    
    except HTTPException:
        raise
    except ImportError as e:
        print(f"[API_ADMIN] Biblioteca não instalada: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Biblioteca necessária não instalada: {str(e)}")
    except Exception as e:
        print(f"[API_ADMIN] Erro ao testar conexão {provider}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao testar conexão: {str(e)}")

@router.put("/llms/{provider}/models/{model}")
async def update_llm_model(provider: str, model: str, model_update: LLMModelUpdate):
    """Ativa ou desativa um modelo específico"""
    try:
        provider_lower = provider.lower()
        model_lower = model.lower()
        
        # Buscar config atual
        result = db.supabase.table("llm_providers").select("*").eq("provider", provider_lower).execute()
        
        current_config = {"enabled_models": []}
        if result.data and len(result.data) > 0:
            current_config = result.data[0].get("config", {}) or {"enabled_models": []}
        
        enabled_models = current_config.get("enabled_models", [])
        
        if model_update.enabled:
            if model_lower not in enabled_models:
                enabled_models.append(model_lower)
        else:
            if model_lower in enabled_models:
                enabled_models.remove(model_lower)
        
        current_config["enabled_models"] = enabled_models
        
        update_data = {
            "config": current_config,
            "updated_at": datetime.now().isoformat()
        }
        
        if result.data and len(result.data) > 0:
            db.supabase.table("llm_providers").update(update_data).eq("provider", provider_lower).execute()
        else:
            update_data["provider"] = provider_lower
            update_data["status"] = "disconnected"
            update_data["created_at"] = datetime.now().isoformat()
            db.supabase.table("llm_providers").insert(update_data).execute()
        
        return {"success": True, "provider": provider_lower, "model": model_lower, "enabled": model_update.enabled}
    except Exception as e:
        print(f"[API_ADMIN] Erro ao atualizar modelo {model}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar modelo: {str(e)}")

@router.get("/llms/usage")
async def get_usage_stats():
    """Retorna estatísticas de uso de LLMs"""
    try:
        # TODO: Implementar estatísticas reais
        return {
            "total_requests": 1234,
            "total_tokens": 89000,
            "total_cost": 2.67,
            "by_provider": {
                "openai": {"requests": 1000, "tokens": 75000, "cost": 2.25},
                "anthropic": {"requests": 200, "tokens": 12000, "cost": 0.36},
                "google": {"requests": 34, "tokens": 2000, "cost": 0.06},
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estatísticas: {str(e)}")

@router.get("/stats")
async def get_dashboard_stats():
    """Retorna estatísticas reais do dashboard"""
    try:
        from datetime import datetime, timedelta
        
        db_instance = get_db()
        
        # Total de agentes ativos
        agents_result = db_instance.supabase.table("agents").select("id").eq("status", "active").execute()
        total_agents = len(agents_result.data) if agents_result.data else 0
        
        # Agentes criados este mês
        now = datetime.now()
        first_day_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        agents_this_month_result = db_instance.supabase.table("agents").select("id").eq("status", "active").gte("created_at", first_day_month.isoformat()).execute()
        agents_this_month = len(agents_this_month_result.data) if agents_this_month_result.data else 0
        
        # Total de debates
        debates_result = db_instance.supabase.table("debates").select("id").execute()
        total_debates = len(debates_result.data) if debates_result.data else 0
        
        # Debates esta semana
        first_day_week = now - timedelta(days=now.weekday())
        first_day_week = first_day_week.replace(hour=0, minute=0, second=0, microsecond=0)
        debates_this_week_result = db_instance.supabase.table("debates").select("id").gte("created_at", first_day_week.isoformat()).execute()
        debates_this_week = len(debates_this_week_result.data) if debates_this_week_result.data else 0
        
        # LLMs configurados (providers conectados na tabela llm_providers)
        llms_providers_result = db_instance.supabase.table("llm_providers").select("provider, config, status").eq("status", "connected").execute()
        unique_providers = set()
        provider_models = {}
        
        if llms_providers_result.data:
            for provider_data in llms_providers_result.data:
                provider = provider_data.get("provider")
                if provider:
                    unique_providers.add(provider)
                    config = provider_data.get("config", {}) or {}
                    enabled_models = config.get("enabled_models", [])
                    if enabled_models:
                        if provider not in provider_models:
                            provider_models[provider] = set()
                        for model in enabled_models:
                            provider_models[provider].add(model)
        
        # Formatar lista de LLMs
        llms_list = []
        for provider in sorted(unique_providers):
            models = list(provider_models.get(provider, []))
            if models:
                # Limitar a 2 modelos para não ficar muito longo
                models_str = ', '.join(models[:2])
                if len(models) > 2:
                    models_str += f" (+{len(models) - 2})"
                llms_list.append(f"{provider.upper()}: {models_str}")
            else:
                llms_list.append(provider.upper())
        
        # Uso de API (simulado por enquanto - poderia rastrear tokens de fato)
        # Por enquanto, retorna um percentual baseado em debates realizados
        # Considerando um limite mensal simulado baseado em debates deste mês
        debates_this_month_result = db_instance.supabase.table("debates").select("id").gte("created_at", first_day_month.isoformat()).execute()
        debates_this_month = len(debates_this_month_result.data) if debates_this_month_result.data else 0
        estimated_monthly_limit = 1000  # Limite simulado
        api_usage_percent = min(100, int((debates_this_month / estimated_monthly_limit) * 100)) if estimated_monthly_limit > 0 else 0
        
        # Atividades recentes (últimas 3 de cada tipo)
        recent_activities = []
        
        # Agentes criados recentemente
        recent_agents = db_instance.supabase.table("agents").select("name, created_at").order("created_at", desc=True).limit(3).execute()
        if recent_agents.data:
            for agent in recent_agents.data:
                recent_activities.append({
                    "type": "agent",
                    "message": f"Novo agente criado: {agent.get('name', 'Agente')}",
                    "created_at": agent.get("created_at")
                })
        
        # Debates iniciados recentemente
        recent_debates = db_instance.supabase.table("debates").select("pergunta, created_at").order("created_at", desc=True).limit(3).execute()
        if recent_debates.data:
            for debate in recent_debates.data:
                debate_pergunta = debate.get('pergunta', 'Debate')
                if len(debate_pergunta) > 30:
                    debate_pergunta = debate_pergunta[:30] + "..."
                recent_activities.append({
                    "type": "debate",
                    "message": f"Debate iniciado: {debate_pergunta}",
                    "created_at": debate.get("created_at")
                })
        
        # LLMs configurados recentemente (usar updated_at ou created_at)
        recent_llms = db_instance.supabase.table("llm_providers").select("provider, updated_at, created_at, status").eq("status", "connected").order("updated_at", desc=True).limit(3).execute()
        if recent_llms.data:
            for llm in recent_llms.data:
                provider = llm.get("provider", "").upper()
                recent_activities.append({
                    "type": "llm",
                    "message": f"LLM configurado: {provider}",
                    "created_at": llm.get("updated_at") or llm.get("created_at")
                })
        
        # Ordenar todas as atividades por data (mais recente primeiro) e pegar as 3 mais recentes
        recent_activities.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        recent_activities = recent_activities[:3]
        
        print(f"[API_ADMIN] Estatísticas: agents={total_agents}, debates={total_debates}, llms={len(unique_providers)}")
        
        return {
            "total_agents": total_agents,
            "agents_this_month": agents_this_month,
            "total_debates": total_debates,
            "debates_this_week": debates_this_week,
            "llms_count": len(unique_providers),
            "llms_list": llms_list if llms_list else ["Nenhum configurado"],
            "api_usage_percent": api_usage_percent,
            "recent_activities": recent_activities
        }
    except Exception as e:
        print(f"[API_ADMIN] Erro ao buscar estatísticas: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estatísticas: {str(e)}")

@router.get("/settings")
async def get_settings():
    """Retorna as configurações gerais do sistema"""
    if not db:
        raise HTTPException(status_code=500, detail="Database não configurado")
    try:
        settings = db.get_system_settings()
        return _build_settings_response(settings)
    except Exception as e:
        print(f"[API_ADMIN] Erro ao buscar settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar configurações: {str(e)}")

@router.put("/settings")
async def update_settings(settings_update: SettingsUpdateRequest):
    """Atualiza limites e configurações gerais"""
    if not db:
        raise HTTPException(status_code=500, detail="Database não configurado")
    payload = _build_settings_update_payload(settings_update)
    if not payload:
        current = db.get_system_settings()
        return _build_settings_response(current)
    try:
        updated = db.update_system_settings(payload)
        return _build_settings_response(updated)
    except Exception as e:
        print(f"[API_ADMIN] Erro ao atualizar settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar configurações: {str(e)}")

@router.get("/debug")
async def debug_info():
    """Endpoint de debug para verificar conexão e dados no Supabase"""
    try:
        db_instance = get_db()
        
        debug_info = {
            "database_connected": True,
            "supabase_url": os.getenv("SUPABASE_URL", "N/A"),
            "service_role_configured": bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY")),
            "tables": {}
        }
        
        # Testar cada tabela
        tables_to_test = ["agents", "llm_providers", "debates", "messages", "system_settings"]
        
        for table_name in tables_to_test:
            try:
                # Tentar buscar alguns registros primeiro
                sample_result = db_instance.supabase.table(table_name).select("*").limit(10).execute()
                sample_data = sample_result.data if sample_result.data else []
                
                # Tentar contar registros (pode não funcionar com RLS, então usamos uma query alternativa)
                try:
                    count_result = db_instance.supabase.table(table_name).select("id", count="exact").execute()
                    count = count_result.count if hasattr(count_result, 'count') and count_result.count is not None else len(sample_data)
                except:
                    # Se count não funcionar, fazer uma query para contar manualmente
                    try:
                        all_result = db_instance.supabase.table(table_name).select("id").execute()
                        count = len(all_result.data) if all_result.data else 0
                    except:
                        count = len(sample_data)  # Fallback para o que conseguimos buscar
                
                debug_info["tables"][table_name] = {
                    "exists": True,
                    "count": count,
                    "sample_count": len(sample_data),
                    "sample_data": sample_data[:2] if sample_data else []  # Apenas 2 primeiros para não ficar muito grande
                }
            except Exception as e:
                error_msg = str(e).lower()
                if "relation" in error_msg and "does not exist" in error_msg:
                    debug_info["tables"][table_name] = {
                        "exists": False,
                        "error": "Tabela não existe"
                    }
                elif "permission denied" in error_msg or "row-level security" in error_msg:
                    debug_info["tables"][table_name] = {
                        "exists": True,
                        "error": "RLS bloqueando acesso (permission denied)",
                        "hint": "Verifique as políticas RLS em supabase_rls_setup.sql"
                    }
                else:
                    debug_info["tables"][table_name] = {
                        "exists": True,
                        "error": str(e)
                    }
        
        return debug_info
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "database_connected": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.get("/debug-old")
async def debug_info():
    """Endpoint de debug para verificar se as rotas estão funcionando"""
    return {
        "status": "ok",
        "router_registered": True,
        "database_connected": db.test_connection() if hasattr(db, 'test_connection') else "unknown",
        "message": "Rotas de admin estão funcionando"
    }

# ========== ENDPOINTS RAG (Base de Conhecimento) ==========

class KnowledgeCreate(BaseModel):
    title: str
    content: str
    file_type: str = "text"

@router.post("/agents/{agent_id}/knowledge")
async def add_agent_knowledge(
    agent_id: str,
    knowledge: KnowledgeCreate
):
    """Adiciona conhecimento/documento para um agente"""
    try:
        from rag_manager import RAGManager
        
        # Verificar se agente existe
        result = db.supabase.table("agents").select("*").eq("id", agent_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Agente nao encontrado")
        
        # Adicionar ao banco
        knowledge_data = {
            "agent_id": agent_id,
            "title": knowledge.title,
            "content": knowledge.content,
            "file_type": knowledge.file_type,
            "metadata": {}
        }
        
        db_result = db.supabase.table("agent_knowledge").insert(knowledge_data).execute()
        knowledge_id = db_result.data[0]["id"]
        
        # Adicionar ao RAG manager
        rag_manager = RAGManager(agent_id, database=db)
        rag_manager.add_document(knowledge.content, knowledge_id=str(knowledge_id), title=knowledge.title)
        
        return {"success": True, "knowledge_id": knowledge_id}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API_ADMIN] Erro ao adicionar conhecimento: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar conhecimento: {str(e)}")

@router.get("/agents/{agent_id}/knowledge")
async def list_agent_knowledge(agent_id: str):
    """Lista todo o conhecimento de um agente"""
    try:
        result = db.supabase.table("agent_knowledge").select("*").eq("agent_id", agent_id).order("created_at", desc=True).execute()
        return {"knowledge": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar conhecimento: {str(e)}")

@router.post("/agents/{agent_id}/knowledge/upload")
async def upload_agent_knowledge_file(
    agent_id: str,
    file: UploadFile = File(...),
    title: str = Form(None)
):
    """Faz upload de um arquivo e adiciona à base de conhecimento do agente"""
    try:
        from rag_manager import RAGManager
        from file_processor import extract_text_from_file
        
        # Verificar se agente existe
        result = db.supabase.table("agents").select("*").eq("id", agent_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Agente nao encontrado")
        
        # Validar tipo de arquivo
        allowed_extensions = ['.txt', '.pdf', '.docx']
        file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Formato de arquivo nao suportado. Formatos permitidos: {', '.join(allowed_extensions)}"
            )
        
        # Ler conteúdo do arquivo
        file_content = await file.read()
        
        # Validar tamanho do arquivo (máximo 100MB)
        if len(file_content) > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Arquivo muito grande. Tamanho máximo: 100MB")
        
        # Extrair texto do arquivo
        try:
            extracted_text = extract_text_from_file(file_content, file.filename)
            if not extracted_text.strip():
                raise HTTPException(status_code=400, detail="Nao foi possivel extrair texto do arquivo. Verifique se o arquivo nao esta vazio ou protegido.")
            
            # Sanitizar o texto para remover caracteres problemáticos (como \u0000)
            # que o PostgreSQL não aceita
            extracted_text = sanitize_text_for_postgres(extracted_text)
            
            if not extracted_text.strip():
                raise HTTPException(status_code=400, detail="O texto extraído do arquivo está vazio após sanitização. O arquivo pode conter apenas caracteres inválidos.")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")
        
        # Usar nome do arquivo como título se não foi fornecido
        document_title = title or file.filename
        
        # Adicionar ao banco
        knowledge_data = {
            "agent_id": agent_id,
            "title": document_title,
            "content": extracted_text,
            "file_type": file_ext[1:] if file_ext else "text",  # Remove o ponto
            "metadata": {
                "original_filename": file.filename,
                "file_size": len(file_content)
            }
        }
        
        db_result = db.supabase.table("agent_knowledge").insert(knowledge_data).execute()
        knowledge_id = db_result.data[0]["id"]
        
        # Adicionar ao RAG manager
        rag_manager = RAGManager(agent_id, database=db)
        rag_manager.add_document(extracted_text, knowledge_id=str(knowledge_id), title=document_title)
        
        print(f"[API_ADMIN] Arquivo {file.filename} adicionado ao conhecimento do agente {agent_id}")
        
        return {
            "success": True, 
            "knowledge_id": knowledge_id,
            "filename": file.filename,
            "text_length": len(extracted_text),
            "title": document_title
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API_ADMIN] Erro ao fazer upload de arquivo: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao fazer upload de arquivo: {str(e)}")

@router.delete("/agents/{agent_id}/knowledge/{knowledge_id}")
async def delete_agent_knowledge(agent_id: str, knowledge_id: str):
    """Remove conhecimento de um agente"""
    try:
        from rag_manager import RAGManager
        
        # Deletar do banco
        db.supabase.table("agent_knowledge").delete().eq("id", knowledge_id).execute()
        db.supabase.table("agent_knowledge_chunks").delete().eq("knowledge_id", knowledge_id).execute()
        
        # Recarregar vector store
        rag_manager = RAGManager(agent_id, database=db)
        rag_manager.reload_from_database()
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar conhecimento: {str(e)}")

