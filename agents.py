"""
Módulo com definições dos agentes bilionários de tech
"""
import os
import sys

# ⚠️ CRÍTICO: Setar env vars ANTES de qualquer import
# Usar assignment direto em vez de setdefault para garantir
os.environ["CREWAI_DISABLE_LITELLM_FALLBACK"] = "true"
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"

# Forçar flush
sys.stdout.flush()

print("[AGENTS] Env vars configuradas ANTES dos imports", flush=True)
print(f"[AGENTS] CREWAI_DISABLE_LITELLM_FALLBACK={os.getenv('CREWAI_DISABLE_LITELLM_FALLBACK')}", flush=True)

# AGORA importar CrewAI
from crewai import Agent
from langchain_openai import ChatOpenAI
from pathlib import Path
from dotenv import load_dotenv

# Carregar .env da raiz do projeto
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configuração do LLM (opcional - não crashar na inicialização)
# As API keys podem ser configuradas pelo admin panel
api_key = os.getenv("OPENAI_API_KEY")
# Ignorar valores placeholder (comum em ambientes de deploy)
if api_key and api_key.lower().strip() in ["placeholder", "none", "", "null"]:
    api_key = None
    llm = None  # Será criado dinamicamente quando necessário
elif api_key:
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=api_key
)
else:
    llm = None  # Será criado dinamicamente quando necessário

def criar_elon_musk():
    """Cria agente representando Elon Musk"""
    # Criar LLM se não existir (para compatibilidade)
    agent_llm = llm
    if agent_llm is None:
        api_key = os.getenv("OPENAI_API_KEY")
        # Ignorar valores placeholder
        if api_key and api_key.lower().strip() in ["placeholder", "none", "", "null"]:
            api_key = None
        if api_key:
            agent_llm = ChatOpenAI(model="gpt-4", temperature=0.7, api_key=api_key)
    
    agent_params = {
        "role": "CEO da Tesla e SpaceX",
        "goal": "Promover inovação disruptiva, sustentabilidade e exploração espacial. Defender visões audaciosas e transformadoras.",
        "backstory": """Você é Elon Musk, um visionário conhecido por suas ideias revolucionárias. 
        Você é direto, às vezes controverso, mas sempre focado em resolver grandes problemas da humanidade.
        Você acredita em inovação rápida, falhas rápidas e aprendizado contínuo. 
        Você gosta de desafiar o status quo e pensar em soluções que outros consideram impossíveis.""",
        "verbose": True,
        "allow_delegation": False
    }
    # Adicionar LLM se disponível
    if agent_llm is not None:
        agent_params["llm"] = agent_llm
    else:
        # Se não há LLM disponível, lançar erro em vez de criar sem LLM
        # Isso evita que o CrewAI tente usar LiteLLM como fallback
        raise ValueError(
            f"Não é possível criar {agent_params['role']} sem LLM. "
            f"Configure uma API key no Admin -> LLMs ou no arquivo .env"
        )
    
    return Agent(**agent_params)

def criar_bill_gates():
    """Cria agente representando Bill Gates"""
    agent_params = {
        "role": "Co-fundador da Microsoft e Filantropo",
        "goal": "Promover impacto social positivo, inovação tecnológica responsável e soluções para problemas globais.",
        "backstory": """Você é Bill Gates, um dos pioneiros da revolução dos computadores pessoais.
        Você é estratégico, pensa em longo prazo e está profundamente comprometido com filantropia.
        Você valoriza dados, evidências e soluções baseadas em ciência.
        Você acredita que a tecnologia deve ser usada para melhorar a vida das pessoas e resolver problemas globais.""",
        "verbose": True,
        "allow_delegation": False
    }
    # Adicionar LLM se disponível
    if llm is not None:
        agent_params["llm"] = llm
    else:
        # Se não há LLM disponível, lançar erro em vez de criar sem LLM
        # Isso evita que o CrewAI tente usar LiteLLM como fallback
        raise ValueError(
            f"Não é possível criar {agent_params['role']} sem LLM. "
            f"Configure uma API key no Admin -> LLMs ou no arquivo .env"
        )
    
    return Agent(**agent_params)

def criar_jeff_bezos():
    """Cria agente representando Jeff Bezos"""
    agent_params = {
        "role": "Fundador da Amazon",
        "goal": "Focar em obsessão pelo cliente, pensamento de longo prazo e inovação contínua.",
        "backstory": """Você é Jeff Bezos, fundador da Amazon e uma das pessoas mais ricas do mundo.
        Você é conhecido por seu pensamento de longo prazo e obsessão pelo cliente.
        Você acredita em 'Day 1' - sempre manter a mentalidade de startup.
        Você valoriza experimentação, aceitação de falhas e aprendizado constante.
        Você pensa em décadas, não em trimestres.""",
        "verbose": True,
        "allow_delegation": False
    }
    # Adicionar LLM se disponível
    if llm is not None:
        agent_params["llm"] = llm
    else:
        # Se não há LLM disponível, lançar erro em vez de criar sem LLM
        # Isso evita que o CrewAI tente usar LiteLLM como fallback
        raise ValueError(
            f"Não é possível criar {agent_params['role']} sem LLM. "
            f"Configure uma API key no Admin -> LLMs ou no arquivo .env"
        )
    
    return Agent(**agent_params)

def criar_mark_zuckerberg():
    """Cria agente representando Mark Zuckerberg"""
    agent_params = {
        "role": "CEO do Meta (Facebook)",
        "goal": "Promover conectividade global, realidade virtual/aumentada e construção de comunidades online.",
        "backstory": """Você é Mark Zuckerberg, fundador do Facebook (agora Meta).
        Você é jovem, ambicioso e acredita no poder de conectar pessoas.
        Você está focado em construir o metaverso e a próxima geração de plataformas sociais.
        Você valoriza inovação rápida, iteração e construção de produtos que bilhões de pessoas usam.
        Você acredita que a tecnologia pode aproximar as pessoas e criar comunidades.""",
        "verbose": True,
        "allow_delegation": False
    }
    # Adicionar LLM se disponível
    if llm is not None:
        agent_params["llm"] = llm
    else:
        # Se não há LLM disponível, lançar erro em vez de criar sem LLM
        # Isso evita que o CrewAI tente usar LiteLLM como fallback
        raise ValueError(
            f"Não é possível criar {agent_params['role']} sem LLM. "
            f"Configure uma API key no Admin -> LLMs ou no arquivo .env"
        )
    
    return Agent(**agent_params)

def criar_tim_cook():
    """Cria agente representando Tim Cook"""
    agent_params = {
        "role": "CEO da Apple",
        "goal": "Promover qualidade, privacidade do usuário, design elegante e sustentabilidade ambiental.",
        "backstory": """Você é Tim Cook, CEO da Apple desde 2011.
        Você é conhecido por sua liderança focada em valores, privacidade e sustentabilidade.
        Você valoriza qualidade sobre quantidade, design cuidadoso e experiência do usuário.
        Você acredita que a tecnologia deve ser intuitiva, acessível e respeitar a privacidade dos usuários.
        Você é mais reservado que outros CEOs, mas é estratégico e focado em excelência.""",
        "verbose": True,
        "allow_delegation": False
    }
    # Adicionar LLM se disponível
    if llm is not None:
        agent_params["llm"] = llm
    else:
        # Se não há LLM disponível, logar warning mas continuar
        print(f"[AGENTS] AVISO: Criando {agent_params['role']} sem LLM específico")
        # CrewAI tentará criar LLM automaticamente (pode falhar)
    
    return Agent(**agent_params)

def criar_facilitador():
    """Cria agente facilitador para síntese de debates"""
    agent_params = {
        "role": "Facilitador e Moderador de Debates",
        "goal": "Sintetizar debates de forma clara, objetiva e estruturada, reunindo todos os pontos discutidos e apresentando conclusões finais.",
        "backstory": """Você é um facilitador experiente e moderador profissional de debates.
        Sua especialidade é analisar discussões complexas, identificar pontos-chave,
        áreas de consenso e divergência, e criar sínteses claras e objetivas.
        Você é neutro, objetivo e focado em ajudar o público a entender as diferentes
        perspectivas apresentadas e chegar a conclusões úteis.""",
        "verbose": True,
        "allow_delegation": False
    }
    
    # Buscar API key para facilitador (prioridade: variável de ambiente específica, depois OPENAI_API_KEY)
    facilitador_api_key = os.getenv("OPENAI_API_KEY_FACILITADOR") or os.getenv("OPENAI_API_KEY")
    
    # Validar que temos uma chave válida
    VALORES_INVALIDOS = ["placeholder", "none", "", "null", "your_key_here", "sua_chave_aqui"]
    if not facilitador_api_key or str(facilitador_api_key).strip().lower() in VALORES_INVALIDOS:
        # Se não houver chave válida, lançar erro
        raise ValueError(
            f"Não é possível criar {agent_params['role']} sem LLM. "
            f"Configure OPENAI_API_KEY_FACILITADOR ou OPENAI_API_KEY no arquivo .env ou no Cloud Run"
        )
    
    # Criar LLM para facilitador com gpt-4.1
    from langchain_openai import ChatOpenAI
    facilitador_llm = ChatOpenAI(
        model="gpt-4.1",
        temperature=0.7,
        api_key=facilitador_api_key
    )
    
    agent_params["llm"] = facilitador_llm
    print("[AGENTS] ✅ Facilitador criado com LLM (gpt-4.1)", flush=True)
    
    return Agent(**agent_params)

# Dicionário com todos os agentes disponíveis
AGENTES_DISPONIVEIS = {
    "Elon Musk": criar_elon_musk,
    "Bill Gates": criar_bill_gates,
    "Jeff Bezos": criar_jeff_bezos,
    "Mark Zuckerberg": criar_mark_zuckerberg,
    "Tim Cook": criar_tim_cook
}

def obter_agente(nome: str) -> Agent:
    """Retorna um agente pelo nome"""
    if nome in AGENTES_DISPONIVEIS:
        return AGENTES_DISPONIVEIS[nome]()
    raise ValueError(f"Agente '{nome}' não encontrado")

def validar_api_key(api_key, provider: str, agent_name: str) -> str:
    """
    Valida API key de forma rigorosa antes de usar.
    Retorna a chave válida ou levanta ValueError com mensagem clara.
    """
    # Lista de valores que devem ser tratados como "sem chave"
    VALORES_INVALIDOS = ["placeholder", "none", "", "null", "your_key_here", "sua_chave_aqui"]
    
    # Verificar se é None ou vazio
    if not api_key:
        raise ValueError(
            f"API key não encontrada para o provedor '{provider}'. "
            f"Configure no Admin -> LLMs ou no arquivo .env. "
            f"Agente: '{agent_name}'"
        )
    
    # Converter para string e limpar
    api_key_str = str(api_key).strip()
    
    # Verificar se é um valor placeholder
    if api_key_str.lower() in VALORES_INVALIDOS:
        raise ValueError(
            f"API key é um valor placeholder para '{provider}'. "
            f"Configure uma chave válida no Admin -> LLMs. "
            f"Agente: '{agent_name}'"
        )
    
    # Verificar tamanho mínimo (API keys geralmente têm 20+ caracteres)
    if len(api_key_str) < 20:
        raise ValueError(
            f"API key muito curta para '{provider}' (tem {len(api_key_str)} caracteres). "
            f"Configure uma chave válida no Admin -> LLMs. "
            f"Agente: '{agent_name}'"
        )
    
    return api_key_str

def criar_agente_dinamico(agent_data: dict, use_rag: bool = True, database=None) -> Agent:
    """Cria um agente dinamicamente a partir de dados do banco"""
    from langchain_anthropic import ChatAnthropic
    from rag_manager import RAGManager
    import os
    from pathlib import Path
    from dotenv import load_dotenv
    
    # Carregar .env
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    
    # Buscar API key: primeiro do banco de dados, depois do .env como fallback
    llm_provider = agent_data.get("llm_provider", "openai").lower()
    agent_name = agent_data.get('name', 'Desconhecido')
    api_key = None
    
    print(f"[AGENTS] Buscando API key para {llm_provider} (agente: {agent_name})")
    
    # Tentar buscar do banco de dados primeiro
    if database:
        try:
            result = database.supabase.table("llm_providers").select("*").eq("provider", llm_provider).execute()
            if result.data and len(result.data) > 0:
                provider_data = result.data[0]
                # Buscar API key se existir, independente do status
                # O status "connected" só indica que foi testada, mas a chave pode existir mesmo sem teste
                if provider_data.get("api_key_encrypted"):
                    api_key = provider_data.get("api_key_encrypted")
                    status = provider_data.get("status", "disconnected")
                    print(f"[AGENTS] Usando API key do banco de dados para {llm_provider} (status: {status})")
        except Exception as e:
            print(f"[AGENTS] Erro ao buscar API key do banco: {str(e)}")
    
    # Fallback para variáveis de ambiente se não encontrou no banco
    if not api_key:
        if llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
        elif llm_provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
        elif llm_provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        
        # Ignorar valores "placeholder", "none" ou vazios - tratá-los como se não existissem
        # Isso permite que o código busque no banco de dados mesmo quando variáveis de ambiente
        # estão definidas com valores placeholder (comum em ambientes de deploy)
        if api_key and api_key.lower().strip() in ["placeholder", "none", "", "null"]:
            api_key = None
            print(f"[AGENTS] Ignorando valor placeholder para {llm_provider}, buscando no banco de dados")
        
        if api_key:
            print(f"[AGENTS] Usando API key do arquivo .env para {llm_provider}")
    
    # VALIDAÇÃO RIGOROSA antes de criar LLM
    try:
        api_key = validar_api_key(api_key, llm_provider, agent_name)
        print(f"[AGENTS] API key validada para {llm_provider}: {api_key[:7]}...{api_key[-4:]}")
    except ValueError as e:
        print(f"[AGENTS] ERRO: {str(e)}")
        raise
    
    # CRÍTICO: Setar env var com chave validada ANTES de criar LLM
    # Isso garante que SDK use a chave do banco, não o "placeholder"
    # Mapear provider para nome correto da env var
    env_var_name = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY"
    }.get(llm_provider, f"{llm_provider.upper()}_API_KEY")
    
    os.environ[env_var_name] = api_key
    print(f"[AGENTS] Env var atualizada: {env_var_name}")
    
    # Obter max_tokens do agent_data (padrão: 1000)
    max_tokens = int(agent_data.get("max_tokens", 1000))
    
    # Configurar LLM baseado no provider
    if llm_provider == "openai":
        llm = ChatOpenAI(
            model=agent_data.get("llm_model", "gpt-4"),
            temperature=float(agent_data.get("temperature", 0.7)),
            max_tokens=max_tokens,
            api_key=api_key
        )
    elif llm_provider == "anthropic":
        llm = ChatAnthropic(
            model=agent_data.get("llm_model", "claude-3-5-sonnet-20241022"),
            temperature=float(agent_data.get("temperature", 0.7)),
            max_tokens=max_tokens,
            api_key=api_key
        )
    elif llm_provider == "google":
        # Estratégia: Tentar múltiplas abordagens em ordem de preferência
        # O CrewAI pode não reconhecer ChatGoogleGenerativeAI, então tentamos várias opções
        llm = None
        last_error = None
        
        # TENTATIVA 1: Usar CrewAI.LLM nativo (melhor compatibilidade)
        try:
            print(f"[AGENTS] Tentativa 1: Criar Google via CrewAI.LLM...", flush=True)
            from crewai import LLM
            
            model_name = agent_data.get("llm_model", "gemini-2.5-flash")
            # Formato esperado pelo CrewAI: "gemini/modelo"
            if not model_name.startswith("gemini/"):
                model_name = f"gemini/{model_name}"
            
            llm = LLM(
                model=model_name,
                temperature=float(agent_data.get("temperature", 0.7)),
                max_tokens=max_tokens,
                api_key=api_key
            )
            print(f"[AGENTS] ✅ Google LLM criado via CrewAI.LLM", flush=True)
        except Exception as e1:
            print(f"[AGENTS] ❌ Tentativa 1 falhou: {e1}", flush=True)
            last_error = e1
            
            # TENTATIVA 2: Usar ChatGoogleGenerativeAI direto
            try:
                print(f"[AGENTS] Tentativa 2: Criar via ChatGoogleGenerativeAI...", flush=True)
            from langchain_google_genai import ChatGoogleGenerativeAI
                
                # Tentar com google_api_key primeiro (versão antiga), depois api_key (versão nova)
                try:
            llm = ChatGoogleGenerativeAI(
                        model=agent_data.get("llm_model", "gemini-2.5-flash"),
                temperature=float(agent_data.get("temperature", 0.7)),
                max_output_tokens=max_tokens,  # Google usa max_output_tokens
                google_api_key=api_key
            )
                except TypeError:
                    # Se google_api_key não funcionar, tentar api_key (versão 2.x)
                    llm = ChatGoogleGenerativeAI(
                        model=agent_data.get("llm_model", "gemini-2.5-flash"),
                        temperature=float(agent_data.get("temperature", 0.7)),
                        max_output_tokens=max_tokens,
                        api_key=api_key
                    )
                print(f"[AGENTS] ✅ Google LLM criado via ChatGoogleGenerativeAI", flush=True)
            except ImportError as e2:
                print(f"[AGENTS] ❌ Tentativa 2 falhou (ImportError): {e2}", flush=True)
                last_error = e2
            except Exception as e2:
                print(f"[AGENTS] ❌ Tentativa 2 falhou: {e2}", flush=True)
                last_error = e2
                
                # TENTATIVA 3: Fallback para OpenAI
                print(f"[AGENTS] Tentativa 3: Fallback para OpenAI...", flush=True)
                try:
                    # Buscar OpenAI API key do banco ou env
                    openai_key = os.getenv("OPENAI_API_KEY")
                    if not openai_key or openai_key.lower().strip() in ["placeholder", "none", "", "null"]:
                        # Tentar buscar do banco
                        if database:
                            result = database.supabase.table("llm_providers").select("*").eq("provider", "openai").execute()
                            if result.data and len(result.data) > 0:
                                openai_key = result.data[0].get("api_key_encrypted")
                    
                    if openai_key and openai_key.lower().strip() not in ["placeholder", "none", "", "null"]:
                        # Validar a chave
                        openai_key = validar_api_key(openai_key, "openai", agent_data.get('name', 'Desconhecido'))
                        # Setar env var
                        os.environ["OPENAI_API_KEY"] = openai_key
                        
                        llm = ChatOpenAI(
                            model="gpt-4",
                            temperature=float(agent_data.get("temperature", 0.7)),
                            max_tokens=max_tokens,
                            api_key=openai_key
                        )
                        print(f"[AGENTS] ⚠️ Usando OpenAI como fallback para Google Gemini", flush=True)
                    else:
                        raise ValueError("OpenAI API key não disponível para fallback")
                except Exception as e3:
                    print(f"[AGENTS] ❌ Todas as tentativas falharam", flush=True)
            raise ValueError(
                        f"Não foi possível criar LLM para Google Gemini. "
                        f"Última tentativa: {last_error}"
            )
        
        if llm is None:
            raise ValueError("LLM não foi criado após todas as tentativas")
    else:
        # Default para OpenAI
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            max_tokens=max_tokens,
            api_key=api_key
        )
    
    # VALIDAÇÃO CRÍTICA DO LLM
    if llm is None:
        agent_name = agent_data.get('name', 'Desconhecido')
        raise ValueError(
            f"ERRO: LLM é None para agente {agent_name}. "
            f"Provider: {llm_provider}, Model: {agent_data.get('llm_model')}. "
            f"Verifique se a API key está configurada corretamente."
        )
    
    print(f"[AGENTS] LLM criado: {type(llm).__name__}", flush=True)
    print(f"[AGENTS] LLM model: {getattr(llm, 'model_name', getattr(llm, 'model', 'N/A'))}", flush=True)
    print(f"[AGENTS] ENV CREWAI_DISABLE_LITELLM_FALLBACK: {os.getenv('CREWAI_DISABLE_LITELLM_FALLBACK')}", flush=True)
    
    # TESTAR LLM ANTES DE PASSAR PARA AGENT
    # Verificar se o LLM tem o método invoke (Runnable do LangChain)
    if hasattr(llm, "invoke"):
        try:
            print(f"[AGENTS] Testando LLM (Runnable)...", flush=True)
            # Teste simples: invocar com uma mensagem mínima
            test_result = llm.invoke("test")
            print(f"[AGENTS] ✅ LLM respondeu ao teste", flush=True)
        except Exception as test_error:
            print(f"[AGENTS] ❌ ERRO: LLM falhou no teste: {test_error}", flush=True)
            import traceback
            traceback.print_exc()
            raise ValueError(f"LLM inválido para agente {agent_name}: {test_error}")
    else:
        # LLM nativo/alternativo (ex: GeminiCompletion do CrewAI) - não precisa de teste de invoke
        print(f"[AGENTS] ⚠️ LLM nativo/alternativo detectado (sem método invoke) - pulando teste de invocação", flush=True)
        print(f"[AGENTS] ✅ LLM considerado válido (tipo: {type(llm).__name__})", flush=True)
    
    # Tratar verbose - pode vir como string do banco
    verbose = agent_data.get("verbose", True)
    if isinstance(verbose, str):
        verbose = verbose.lower() in ("true", "1", "yes", "on")
    elif verbose is None:
        verbose = True
    
    # Tratar allow_delegation - pode vir como string do banco
    allow_delegation = agent_data.get("allow_delegation", False)
    if isinstance(allow_delegation, str):
        allow_delegation = allow_delegation.lower() in ("true", "1", "yes", "on")
    elif allow_delegation is None:
        allow_delegation = False
    
    # Criar backstory base
    base_backstory = agent_data.get("backstory", "")
    
    # Se RAG estiver habilitado, adicionar instrução
    if use_rag:
        rag_instruction = """
        
        IMPORTANTE: Você tem acesso a uma base de conhecimento personalizada com informações relevantes.
        Quando necessário, use essas informações para enriquecer suas respostas e argumentos.
        Sempre priorize informações da sua base de conhecimento quando forem relevantes ao tópico discutido.
        """
        backstory = base_backstory + rag_instruction
    else:
        backstory = base_backstory
    
    # Criar agent com LLM (já validamos que não é None)
    agent_params = {
        "role": agent_data.get("role", ""),
        "goal": agent_data.get("goal", ""),
        "backstory": backstory,
        "verbose": verbose,
        "allow_delegation": allow_delegation,
        "llm": llm  # Sempre passar - já validamos e testamos
    }
    
    print(f"[AGENTS] Criando Agent com LLM validado...", flush=True)
    print(f"[AGENTS] agent_params keys: {list(agent_params.keys())}", flush=True)
    print(f"[AGENTS] LLM type: {type(agent_params.get('llm'))}", flush=True)
    
    # AGORA criar Agent com LLM validado
    try:
        agent = Agent(**agent_params)
        print(f"[AGENTS] ✅ Agent criado com sucesso", flush=True)
    except Exception as agent_error:
        print(f"[AGENTS] ❌ ERRO ao criar Agent: {agent_error}", flush=True)
        print(f"[AGENTS] agent_params keys: {list(agent_params.keys())}", flush=True)
        print(f"[AGENTS] LLM type: {type(agent_params.get('llm'))}", flush=True)
        print(f"[AGENTS] LLM object: {agent_params.get('llm')}", flush=True)
        import traceback
        traceback.print_exc()
        raise
    
    # Não podemos adicionar atributos ao Agent (é um modelo Pydantic)
    # O RAG manager será gerenciado externamente via dicionário
    
    return agent

