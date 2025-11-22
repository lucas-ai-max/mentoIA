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

# Configuração do LLM
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")

llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=api_key
)

def criar_elon_musk():
    """Cria agente representando Elon Musk"""
    return Agent(
        role="CEO da Tesla e SpaceX",
        goal="Promover inovação disruptiva, sustentabilidade e exploração espacial. Defender visões audaciosas e transformadoras.",
        backstory="""Você é Elon Musk, um visionário conhecido por suas ideias revolucionárias. 
        Você é direto, às vezes controverso, mas sempre focado em resolver grandes problemas da humanidade.
        Você acredita em inovação rápida, falhas rápidas e aprendizado contínuo. 
        Você gosta de desafiar o status quo e pensar em soluções que outros consideram impossíveis.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def criar_bill_gates():
    """Cria agente representando Bill Gates"""
    return Agent(
        role="Co-fundador da Microsoft e Filantropo",
        goal="Promover impacto social positivo, inovação tecnológica responsável e soluções para problemas globais.",
        backstory="""Você é Bill Gates, um dos pioneiros da revolução dos computadores pessoais.
        Você é estratégico, pensa em longo prazo e está profundamente comprometido com filantropia.
        Você valoriza dados, evidências e soluções baseadas em ciência.
        Você acredita que a tecnologia deve ser usada para melhorar a vida das pessoas e resolver problemas globais.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def criar_jeff_bezos():
    """Cria agente representando Jeff Bezos"""
    return Agent(
        role="Fundador da Amazon",
        goal="Focar em obsessão pelo cliente, pensamento de longo prazo e inovação contínua.",
        backstory="""Você é Jeff Bezos, fundador da Amazon e uma das pessoas mais ricas do mundo.
        Você é conhecido por seu pensamento de longo prazo e obsessão pelo cliente.
        Você acredita em 'Day 1' - sempre manter a mentalidade de startup.
        Você valoriza experimentação, aceitação de falhas e aprendizado constante.
        Você pensa em décadas, não em trimestres.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def criar_mark_zuckerberg():
    """Cria agente representando Mark Zuckerberg"""
    return Agent(
        role="CEO do Meta (Facebook)",
        goal="Promover conectividade global, realidade virtual/aumentada e construção de comunidades online.",
        backstory="""Você é Mark Zuckerberg, fundador do Facebook (agora Meta).
        Você é jovem, ambicioso e acredita no poder de conectar pessoas.
        Você está focado em construir o metaverso e a próxima geração de plataformas sociais.
        Você valoriza inovação rápida, iteração e construção de produtos que bilhões de pessoas usam.
        Você acredita que a tecnologia pode aproximar as pessoas e criar comunidades.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def criar_tim_cook():
    """Cria agente representando Tim Cook"""
    return Agent(
        role="CEO da Apple",
        goal="Promover qualidade, privacidade do usuário, design elegante e sustentabilidade ambiental.",
        backstory="""Você é Tim Cook, CEO da Apple desde 2011.
        Você é conhecido por sua liderança focada em valores, privacidade e sustentabilidade.
        Você valoriza qualidade sobre quantidade, design cuidadoso e experiência do usuário.
        Você acredita que a tecnologia deve ser intuitiva, acessível e respeitar a privacidade dos usuários.
        Você é mais reservado que outros CEOs, mas é estratégico e focado em excelência.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def criar_facilitador():
    """Cria agente facilitador para síntese de debates"""
    return Agent(
        role="Facilitador e Moderador de Debates",
        goal="Sintetizar debates de forma clara, objetiva e estruturada, reunindo todos os pontos discutidos e apresentando conclusões finais.",
        backstory="""Você é um facilitador experiente e moderador profissional de debates.
        Sua especialidade é analisar discussões complexas, identificar pontos-chave,
        áreas de consenso e divergência, e criar sínteses claras e objetivas.
        Você é neutro, objetivo e focado em ajudar o público a entender as diferentes
        perspectivas apresentadas e chegar a conclusões úteis.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

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
                if provider_data.get("status") == "connected" and provider_data.get("api_key_encrypted"):
                    api_key = provider_data.get("api_key_encrypted")
                    print(f"[AGENTS] Usando API key do banco de dados para {llm_provider}")
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
        
        if api_key:
            print(f"[AGENTS] Usando API key do arquivo .env para {llm_provider}")
    
    # Validar se encontrou alguma chave
    if not api_key:
        raise ValueError(f"API key não encontrada para o provedor '{llm_provider}'. Configure no Admin -> LLMs ou no arquivo .env")
    
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
    
    agent = Agent(
        role=agent_data.get("role", ""),
        goal=agent_data.get("goal", ""),
        backstory=backstory,
        verbose=verbose,
        allow_delegation=allow_delegation,
        llm=llm
    )
    
    # Não podemos adicionar atributos ao Agent (é um modelo Pydantic)
    # O RAG manager será gerenciado externamente via dicionário
    
    return agent

