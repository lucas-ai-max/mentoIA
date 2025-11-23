"""
Módulo com definições dos agentes bilionários de tech
"""
from crewai import Agent
from langchain_openai import ChatOpenAI
import os
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
if api_key:
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7,
        api_key=api_key
    )
else:
    # LLM será criado dinamicamente quando necessário
    llm = None

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
    # Só adicionar llm se não for None (evita que CrewAI tente criar automaticamente)
    if agent_llm is not None:
        agent_params["llm"] = agent_llm
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
    # Só adicionar llm se não for None (evita que CrewAI tente criar automaticamente)
    if llm is not None:
        agent_params["llm"] = llm
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
    # Só adicionar llm se não for None (evita que CrewAI tente criar automaticamente)
    if llm is not None:
        agent_params["llm"] = llm
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
    # Só adicionar llm se não for None (evita que CrewAI tente criar automaticamente)
    if llm is not None:
        agent_params["llm"] = llm
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
    # Só adicionar llm se não for None (evita que CrewAI tente criar automaticamente)
    if llm is not None:
        agent_params["llm"] = llm
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
    # Só adicionar llm se não for None (evita que CrewAI tente criar automaticamente)
    if llm is not None:
        agent_params["llm"] = llm
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

def criar_agente_dinamico(agent_data: dict, use_rag: bool = True, database=None) -> Agent:
    """Cria um agente dinamicamente a partir de dados do banco"""
    from langchain_openai import ChatOpenAI
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
    api_key = None
    
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
    
    # Validar se encontrou alguma chave (mais rigoroso)
    if not api_key or not str(api_key).strip():
        agent_name = agent_data.get('name', 'Desconhecido')
        raise ValueError(
            f"API key não encontrada para o provedor '{llm_provider}'. "
            f"Configure no Admin -> LLMs (seção 'Provedores LLM') ou no arquivo .env. "
            f"O agente '{agent_name}' precisa de uma API key válida para funcionar."
        )
    
    # Garantir que api_key não seja vazio após strip
    api_key = str(api_key).strip()
    if not api_key or len(api_key) < 10:  # API keys geralmente têm mais de 10 caracteres
        agent_name = agent_data.get('name', 'Desconhecido')
        raise ValueError(
            f"API key inválida para o provedor '{llm_provider}'. "
            f"A chave parece estar vazia ou muito curta. Configure no Admin -> LLMs. "
            f"Agente: '{agent_name}'"
        )
    
    # Obter max_tokens do agent_data (padrão: 1000)
    max_tokens = int(agent_data.get("max_tokens", 1000))
    
    # Configurar LLM baseado no provider
    if llm_provider == "openai":
        # Validar novamente antes de criar (segurança extra)
        if not api_key or len(api_key) < 10:
            agent_name = agent_data.get('name', 'Desconhecido')
            raise ValueError(
                f"API key inválida para OpenAI. Configure no Admin -> LLMs. "
                f"Agente: '{agent_name}'"
            )
        
        llm = ChatOpenAI(
            model=agent_data.get("llm_model", "gpt-4"),
            temperature=float(agent_data.get("temperature", 0.7)),
            max_tokens=max_tokens,
            api_key=api_key
        )
    elif llm_provider == "anthropic":
        # Validar novamente antes de criar (segurança extra)
        if not api_key or len(api_key) < 10:
            agent_name = agent_data.get('name', 'Desconhecido')
            raise ValueError(
                f"API key inválida para Anthropic. Configure no Admin -> LLMs. "
                f"Agente: '{agent_name}'"
            )
        
        llm = ChatAnthropic(
            model=agent_data.get("llm_model", "claude-3-5-sonnet-20241022"),
            temperature=float(agent_data.get("temperature", 0.7)),
            max_tokens=max_tokens,
            api_key=api_key
        )
    elif llm_provider == "google":
        # Validar novamente antes de criar (segurança extra)
        if not api_key or len(api_key) < 10:
            agent_name = agent_data.get('name', 'Desconhecido')
            raise ValueError(
                f"API key inválida para Google. Configure no Admin -> LLMs. "
                f"Agente: '{agent_name}'"
            )
        
        # Google Gemini - suporte básico (precisa de biblioteca adicional)
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            # Tentar com google_api_key primeiro (versão antiga), depois api_key (versão nova)
            try:
                llm = ChatGoogleGenerativeAI(
                    model=agent_data.get("llm_model", "gemini-pro"),
                    temperature=float(agent_data.get("temperature", 0.7)),
                    max_output_tokens=max_tokens,  # Google usa max_output_tokens
                    google_api_key=api_key
                )
            except TypeError:
                # Se google_api_key não funcionar, tentar api_key (versão 2.x)
                llm = ChatGoogleGenerativeAI(
                    model=agent_data.get("llm_model", "gemini-pro"),
                    temperature=float(agent_data.get("temperature", 0.7)),
                    max_output_tokens=max_tokens,
                    api_key=api_key
                )
        except ImportError:
            raise ValueError(
                "Google Gemini requer 'langchain-google-genai'. "
                "Instale com: pip install langchain-google-genai"
            )
        except Exception as e:
            raise ValueError(f"Erro ao configurar Google Gemini: {str(e)}")
    else:
        # Validar novamente antes de criar (segurança extra)
        if not api_key or len(api_key) < 10:
            agent_name = agent_data.get('name', 'Desconhecido')
            raise ValueError(
                f"API key inválida para o provedor '{llm_provider}'. Configure no Admin -> LLMs. "
                f"Agente: '{agent_name}'"
            )
        
        # Default para OpenAI
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            max_tokens=max_tokens,
            api_key=api_key
        )
    
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
    
    # Só passar llm se não for None (evita que CrewAI tente criar automaticamente)
    agent_params = {
        "role": agent_data.get("role", ""),
        "goal": agent_data.get("goal", ""),
        "backstory": backstory,
        "verbose": verbose,
        "allow_delegation": allow_delegation
    }
    # Só adicionar llm se não for None (evita que CrewAI tente criar automaticamente)
    if llm is not None:
        agent_params["llm"] = llm
    
    agent = Agent(**agent_params)
    
    # Não podemos adicionar atributos ao Agent (é um modelo Pydantic)
    # O RAG manager será gerenciado externamente via dicionário
    
    return agent

