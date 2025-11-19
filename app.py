"""
Interface Streamlit para Mesa de Debates
"""
import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar .env da raiz do projeto antes de importar outros módulos
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from agents import AGENTES_DISPONIVEIS
from debate_crew import DebateCrew

# Configuração da página
st.set_page_config(
    page_title="Mesa de Debates - Bilionários de Tech",
    page_icon="🚀",
    layout="wide"
)

# Verificar se API key está configurada
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ Por favor, configure sua OPENAI_API_KEY no arquivo .env")
    st.stop()

# Título principal
st.title("🚀 Mesa de Debates - Bilionários de Tech")
st.markdown("---")

# Sidebar para seleção de agentes
with st.sidebar:
    st.header("⚙️ Configurações do Debate")
    
    st.subheader("👥 Selecionar Participantes")
    st.caption("Escolha quais bilionários participarão do debate (mínimo 2)")
    
    agentes_selecionados = []
    for nome_agente in AGENTES_DISPONIVEIS.keys():
        if st.checkbox(nome_agente, key=f"checkbox_{nome_agente}"):
            agentes_selecionados.append(nome_agente)
    
    st.markdown("---")
    
    st.subheader("🎛️ Configurações")
    num_rodadas = st.slider(
        "Número de Rodadas",
        min_value=1,
        max_value=5,
        value=2,
        help="Cada rodada permite que todos os agentes falem uma vez"
    )
    
    st.markdown("---")
    
    # Informações sobre os agentes
    with st.expander("ℹ️ Sobre os Agentes"):
        st.markdown("""
        **Elon Musk** - Visionário, disruptivo, focado em inovação
        
        **Bill Gates** - Filantropo, estratégico, focado em impacto social
        
        **Jeff Bezos** - Focado em longo prazo, orientado ao cliente
        
        **Mark Zuckerberg** - Focado em conectividade e metaverso
        
        **Tim Cook** - Focado em qualidade, privacidade e sustentabilidade
        """)

# Área principal do chat
st.subheader("💬 Área do Debate")

# Inicializar histórico na sessão
if "historico_debates" not in st.session_state:
    st.session_state.historico_debates = []

# Exibir histórico anterior
if st.session_state.historico_debates:
    st.markdown("### 📜 Histórico de Debates")
    for i, debate in enumerate(st.session_state.historico_debates):
        with st.expander(f"Debate #{i+1}: {debate['pergunta'][:50]}..."):
            st.markdown(debate['resultado'])
    st.markdown("---")

# Input da pergunta
pergunta = st.text_area(
    "🤔 Faça sua pergunta para os bilionários:",
    placeholder="Ex: Qual é o futuro da inteligência artificial?",
    height=100
)

# Botão para iniciar debate
col1, col2 = st.columns([1, 4])

with col1:
    iniciar_debate = st.button("🚀 Iniciar Debate", type="primary", use_container_width=True)

# Validações
if iniciar_debate:
    if len(agentes_selecionados) < 2:
        st.error("⚠️ Selecione pelo menos 2 agentes para o debate!")
    elif not pergunta.strip():
        st.error("⚠️ Por favor, digite uma pergunta!")
    else:
        # Mostrar loading
        with st.spinner("🔄 Os bilionários estão debatendo... Isso pode levar alguns momentos."):
            try:
                # Criar e executar debate
                debate = DebateCrew(agentes_selecionados, pergunta)
                historico = debate.executar_debate(num_rodadas=num_rodadas)
                resultado_formatado = debate.obter_historico_formatado()
                
                # Salvar no histórico
                st.session_state.historico_debates.append({
                    "pergunta": pergunta,
                    "agentes": agentes_selecionados,
                    "resultado": resultado_formatado
                })
                
                # Exibir resultado
                st.markdown("### 🎯 Resultado do Debate")
                st.markdown(resultado_formatado)
                
                st.success("✅ Debate concluído com sucesso!")
                
            except Exception as e:
                st.error(f"❌ Erro ao executar debate: {str(e)}")
                st.exception(e)

# Footer
st.markdown("---")
st.caption("💡 Dica: Selecione diferentes combinações de agentes para ver diferentes perspectivas sobre o mesmo tema!")

