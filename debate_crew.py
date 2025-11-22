"""
Módulo com a lógica de orquestração do debate
"""
from crewai import Crew, Process, Task, Agent
from agents import obter_agente, AGENTES_DISPONIVEIS
from typing import List, Dict, Optional, Any
import time

class DebateCrew:
    """Classe para gerenciar debates entre agentes"""
    
    def __init__(
        self,
        nomes_agentes: List[str] = None,
        pergunta: str = None,
        agentes_crewai: List[Agent] = None,
        rag_managers: Optional[Dict[int, Any]] = None,
        contexto_usuario: Optional[List[str]] = None,
        modo: str = 'debate'
    ):
        """
        Inicializa o debate
        
        Args:
            nomes_agentes: Lista com nomes dos agentes participantes (modo compatibilidade)
            pergunta: A questão a ser debatida
            agentes_crewai: Lista opcional de agentes CrewAI já criados (modo dinâmico)
            rag_managers: Dicionário opcional mapeando índice do agente -> RAGManager
        """
        if not pergunta:
            raise ValueError("Pergunta é obrigatória")
        
        self.pergunta = pergunta
        self.rag_managers = rag_managers or {}  # Dicionário: índice -> RAGManager
        self.contexto_usuario = contexto_usuario or []
        self.modo = modo
        self.should_generate_summary = self.modo == 'sintese'
        
        if agentes_crewai:
            # Modo dinâmico: usar agentes já criados
            if not agentes_crewai or len(agentes_crewai) == 0:
                raise ValueError("Lista de agentes não pode estar vazia")
            self.agentes = agentes_crewai
        elif nomes_agentes:
            # Modo compatibilidade: criar agentes pelos nomes
            if not nomes_agentes or len(nomes_agentes) == 0:
                raise ValueError("Lista de nomes de agentes não pode estar vazia")
            self.agentes = [obter_agente(nome) for nome in nomes_agentes]
        else:
            raise ValueError("É necessário fornecer nomes_agentes ou agentes_crewai")
        self.historico = []
        
    def executar_debate(self, num_rodadas: int = 3) -> List[Dict]:
        """
        Executa o debate entre os agentes
        
        Args:
            num_rodadas: Número de rodadas de debate (cada agente fala uma vez por rodada)
            
        Returns:
            Lista com o histórico do debate
        """
        historico = []
        if self.should_generate_summary:
            historico = [{
                "tipo": "pergunta",
                "conteudo": self.pergunta,
                "agente": "Contexto"
            }] + self._build_history_from_context()
            self.historico = historico
            sintese_final = self.gerar_sintese_com_agente()
            historico.append({
                "tipo": "sintese_conteudo",
                "conteudo": sintese_final,
                "agente": "Facilitador"
            })
            self.historico = historico
            return historico
        contexto_usuario_block = ""
        if self.contexto_usuario:
            contexto_usuario_block = "\nContexto adicional fornecido pelo usuário:\n" + "\n".join(self.contexto_usuario)
        
        # Mensagem inicial com a pergunta
        historico.append({
            "tipo": "pergunta",
            "conteudo": self.pergunta,
            "agente": "Moderador"
        })
        
        # Cada agente responde uma vez
        for idx, agente in enumerate(self.agentes):
                try:
                    # Contexto: o que outros agentes já disseram
                    contexto_anterior = self._obter_contexto_anterior(historico)
                    
                    # Buscar contexto RAG se disponível (usando índice do agente)
                    rag_context = ""
                    if idx in self.rag_managers:
                        rag_manager = self.rag_managers[idx]
                        if rag_manager:
                            rag_context = rag_manager.get_context(self.pergunta, k=2)
                    
                    # Criar prompt com contexto RAG
                    if rag_context:
                        enhanced_prompt = f"""
                        Você está participando de um debate sobre: {self.pergunta}
                        
                        Contexto do debate até agora:
                        {contexto_anterior}
                        {contexto_usuario_block}
                        
                        Informações relevantes da sua base de conhecimento:
                        {rag_context}
                        
                        Agora é sua vez de falar. Dê sua opinião sobre a questão, 
                        considerando o que outros participantes já disseram e as informações 
                        da sua base de conhecimento quando relevantes.
                        Você pode concordar, discordar ou adicionar novas perspectivas.
                        Seja autêntico à sua personalidade e estilo de comunicação.
                        Mantenha sua resposta concisa mas impactante (2-3 parágrafos).
                        """
                    else:
                        enhanced_prompt = f"""
                        Você está participando de um debate sobre: {self.pergunta}
                        
                        Contexto do debate até agora:
                        {contexto_anterior}
                        {contexto_usuario_block}
                        
                        Agora é sua vez de falar. Dê sua opinião sobre a questão, 
                        considerando o que outros participantes já disseram. 
                        Você pode concordar, discordar ou adicionar novas perspectivas.
                        Seja autêntico à sua personalidade e estilo de comunicação.
                        Mantenha sua resposta concisa mas impactante (2-3 parágrafos).
                        """
                    
                    task = Task(
                        description=enhanced_prompt,
                        agent=agente,
                        expected_output="Uma resposta clara e autêntica sobre a questão do debate"
                    )
                    
                    # Executa a task
                    crew = Crew(
                        agents=[agente],
                        tasks=[task],
                        process=Process.sequential,
                        verbose=True
                    )
                    
                    resultado = crew.kickoff()
                    
                    historico.append({
                        "tipo": "resposta",
                        "conteudo": str(resultado),
                        "agente": agente.role
                    })
                    
                    # Pequena pausa para tornar o debate mais natural
                    time.sleep(1)
                    
                except Exception as e:
                    historico.append({
                        "tipo": "erro",
                        "conteudo": f"Erro ao processar resposta de {agente.role}: {str(e)}",
                        "agente": "Sistema"
                    })
        
        # Atualizar histórico ANTES de gerar síntese (se necessário)
        self.historico = historico
        
        # Só gerar síntese se should_generate_summary for True (modo 'sintese')
        if self.should_generate_summary:
            print("🔄 Gerando síntese final do debate com agente facilitador...")
            sintese = self.gerar_sintese_com_agente()
            print(f"✅ Síntese gerada: {len(sintese)} caracteres")
            
            # Adicionar apenas o conteúdo da síntese, sem título
            historico.append({
                "tipo": "sintese_conteudo",
                "conteudo": sintese,
                "agente": "Facilitador"
            })
        
        # Atualizar histórico final
        self.historico = historico
        return historico
    
    def gerar_sintese_com_agente(self) -> str:
        """Gera síntese usando um agente facilitador como task"""
        from agents import criar_facilitador
        
        try:
            # Criar agente facilitador
            print("📋 Criando agente facilitador...")
            facilitador = criar_facilitador()
            
            # Compilar todo o debate
            print("📝 Compilando histórico do debate...")
            debate_completo = self.obter_historico_formatado()
            print(f"📊 Histórico compilado: {len(debate_completo)} caracteres")
            contexto_usuario_section = ""
            if self.contexto_usuario:
                contexto_usuario_section = (
                    "CONTEXTO ADICIONAL DO USUÁRIO:\n"
                    + "\n".join(self.contexto_usuario)
                    + "\n\n"
                )
            
            # Criar task para o facilitador
            task_sintese = Task(
                description=f"""
                Você é um facilitador experiente. Analise o seguinte debate e crie uma síntese final completa.
                
                PERGUNTA DO DEBATE: {self.pergunta}
                
                DEBATE COMPLETO:
                {contexto_usuario_section}{debate_completo}
                
                Sua tarefa é criar uma síntese profissional que:
                1. Resuma os principais pontos levantados por cada participante
                2. Identifique áreas de consenso e divergência entre os participantes
                3. Destaque os argumentos mais relevantes e impactantes
                4. Apresente conclusões ou insights finais úteis para o usuário
                5. Seja clara, concisa e objetiva (3-4 parágrafos bem estruturados)
                
                Formate a síntese de forma profissional e estruturada, facilitando o entendimento
                do usuário sobre todos os aspectos discutidos no debate.
                """,
                agent=facilitador,
                expected_output="Uma síntese completa e estruturada do debate, com todos os pontos principais e conclusões finais"
            )
            
            # Executar task com CrewAI
            print("🚀 Executando task de síntese com CrewAI...")
            crew = Crew(
                agents=[facilitador],
                tasks=[task_sintese],
                process=Process.sequential,
                verbose=True
            )
            
            resultado = crew.kickoff()
            print(f"📦 Resultado recebido do CrewAI: {type(resultado)}")
            
            # Extrair conteúdo do resultado
            if hasattr(resultado, 'raw'):
                sintese_texto = str(resultado.raw)
            elif hasattr(resultado, 'content'):
                sintese_texto = str(resultado.content)
            else:
                sintese_texto = str(resultado)
            
            print(f"✅ Síntese extraída: {len(sintese_texto)} caracteres")
            return sintese_texto
            
        except Exception as e:
            error_msg = f"Erro ao gerar síntese: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return error_msg
    
    def _obter_contexto_anterior(self, historico: List[Dict]) -> str:
        """Extrai o contexto das respostas anteriores"""
        contexto = []
        for item in historico:
            if item["tipo"] == "resposta":
                contexto.append(f"{item['agente']}: {item['conteudo']}")
        
        if not contexto:
            return "Este é o início do debate. Seja o primeiro a dar sua opinião."
        
        return "\n".join(contexto[-len(self.agentes):])  # Últimas respostas

    def _build_history_from_context(self) -> List[Dict]:
        historico = []
        for entry in self.contexto_usuario:
            agente, sep, conteudo = entry.partition(': ')
            historico.append({
                "tipo": "resposta",
                "conteudo": conteudo if conteudo else entry,
                "agente": agente if agente else "Contexto"
            })
        return historico
    
    def obter_historico_formatado(self) -> str:
        """Retorna o histórico formatado para exibição (sem síntese)"""
        if not self.historico:
            return "Nenhum debate realizado ainda."
        
        formato = []
        for item in self.historico:
            # Ignorar síntese no histórico formatado (será gerada separadamente)
            if item["tipo"] in ["sintese", "sintese_conteudo"]:
                continue
            if item["tipo"] == "pergunta":
                formato.append(f"**🤔 PERGUNTA:** {item['conteudo']}\n")
            elif item["tipo"] == "resposta":
                formato.append(f"**{item['agente']}:**\n{item['conteudo']}\n")
            elif item["tipo"] == "erro":
                formato.append(f"⚠️ {item['conteudo']}\n")
        
        return "\n".join(formato)

