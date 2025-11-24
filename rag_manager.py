"""
Módulo para gerenciar RAG (Retrieval-Augmented Generation) por agente usando Supabase com pgvector
"""
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from typing import List, Dict, Optional
import os
from pathlib import Path
from dotenv import load_dotenv
import json
import numpy as np

# Carregar .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class RAGManager:
    def __init__(self, agent_id: str, database=None):
        self.agent_id = agent_id
        self.database = database
        
        # Buscar chave da OpenAI para RAG (embeddings)
        # Prioridade: 1) Variáveis de ambiente, 2) Banco de dados (se database fornecido)
        api_key = os.getenv("OPENAI_API_KEY_RAG") or os.getenv("OPENAI_API_KEY")
        
        # Validar se a chave da variável de ambiente é inválida
        VALORES_INVALIDOS = ["placeholder", "none", "", "null", "your_key_here", "sua_chave_aqui"]
        api_key_invalida = not api_key or str(api_key).strip().lower() in VALORES_INVALIDOS
        
        # Se a chave da variável de ambiente for inválida E database fornecido, buscar do banco
        if api_key_invalida and self.database:
            print(f"[RAG] Chave da variável de ambiente inválida ou não encontrada, buscando do banco de dados...")
            try:
                result = self.database.supabase.table("llm_providers").select("*").eq("provider", "openai").execute()
                if result.data and len(result.data) > 0:
                    provider_data = result.data[0]
                    db_api_key = provider_data.get("api_key_encrypted")
                    if db_api_key and str(db_api_key).strip().lower() not in VALORES_INVALIDOS:
                        api_key = db_api_key
                        status = provider_data.get("status", "disconnected")
                        print(f"[RAG] ✅ Chave recuperada do banco de dados (status: {status}) para embeddings (agente: {self.agent_id})")
                    else:
                        print(f"[RAG] ⚠️ Chave encontrada no banco mas é inválida ou placeholder")
                else:
                    print(f"[RAG] ⚠️ Nenhum registro encontrado na tabela llm_providers para provider='openai'")
            except Exception as e:
                print(f"[RAG] ⚠️ Erro ao buscar API key do banco de dados: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Validar que temos uma chave válida
        if not api_key or str(api_key).strip().lower() in VALORES_INVALIDOS:
            raise ValueError(
                "API key da OpenAI não encontrada para embeddings do RAG. "
                "Configure a variável de ambiente OPENAI_API_KEY_RAG ou OPENAI_API_KEY "
                "no Cloud Run ou no arquivo .env, ou configure no Admin -> LLMs no banco de dados."
            )
        
        api_key = str(api_key).strip()
        if len(api_key) < 20:
            raise ValueError(
                f"API key da OpenAI inválida para embeddings (muito curta: {len(api_key)} caracteres). "
                "Configure uma chave válida no Cloud Run, no arquivo .env ou no Admin -> LLMs."
            )
        
        # Log indicando a origem da chave (só se não foi logado antes)
        if not api_key_invalida or not self.database:
            print(f"[RAG] Usando chave da variável de ambiente para embeddings (agente: {self.agent_id})")
        
        # CRÍTICO: Setar env var com chave ANTES de criar embeddings
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Criar embeddings com a chave
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=api_key
        )
        print(f"[RAG] Embeddings inicializados com sucesso")
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        # Não usa mais FAISS - tudo no Supabase
    
    def add_document(self, content: str, knowledge_id: str, title: str = "", metadata: Optional[Dict] = None) -> bool:
        """Adiciona um documento à base de conhecimento do agente no Supabase"""
        if not self.database:
            print("[RAG] Erro: Database não disponível")
            return False
        
        try:
            # Criar documento
            doc_metadata = metadata or {}
            doc_metadata["knowledge_id"] = knowledge_id
            doc_metadata["title"] = title
            
            doc = Document(
                page_content=content,
                metadata=doc_metadata
            )
            
            # Dividir em chunks
            chunks = self.text_splitter.split_documents([doc])
            
            # Gerar embeddings e salvar no Supabase
            for i, chunk in enumerate(chunks):
                # Gerar embedding
                embedding = self.embeddings.embed_query(chunk.page_content)
                
                # Salvar chunk com embedding no Supabase
                # O Supabase aceita lista Python diretamente e converte para vector
                chunk_data = {
                    "knowledge_id": knowledge_id,
                    "chunk_text": chunk.page_content,
                    "chunk_index": i,
                    "embedding": embedding,  # Lista Python será convertida para vector(1536)
                    "metadata": chunk.metadata,
                    "agent_id": self.agent_id  # Adicionar agent_id diretamente
                }
                
                self.database.supabase.table("agent_knowledge_chunks").insert(chunk_data).execute()
            
            print(f"[RAG] Documento adicionado para agente {self.agent_id} ({len(chunks)} chunks)")
            return True
        except Exception as e:
            print(f"[RAG] Erro ao adicionar documento: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def search(self, query: str, k: int = 3) -> List[Document]:
        """Busca documentos relevantes usando busca vetorial no Supabase"""
        if not self.database:
            return []
        
        try:
            # Gerar embedding da query
            query_embedding = self.embeddings.embed_query(query)
            
            # Tentar usar função RPC otimizada primeiro
            try:
                result = self.database.supabase.rpc(
                    'match_chunks',
                    {
                        'query_embedding': query_embedding,
                        'match_count': k,
                        'agent_id': self.agent_id
                    }
                ).execute()
                
                if result.data:
                    # Converter para Document objects
                    documents = []
                    for chunk in result.data:
                        # Buscar título do documento original
                        title = "Documento"
                        if chunk.get('knowledge_id'):
                            try:
                                knowledge_result = self.database.supabase.table("agent_knowledge").select("title").eq("id", chunk['knowledge_id']).execute()
                                if knowledge_result.data:
                                    title = knowledge_result.data[0].get('title', 'Documento')
                            except:
                                pass
                        
                        metadata = chunk.get('metadata', {})
                        metadata['title'] = title
                        metadata['knowledge_id'] = chunk.get('knowledge_id')
                        
                        documents.append(Document(
                            page_content=chunk['chunk_text'],
                            metadata=metadata
                        ))
                    
                    return documents
            except Exception as rpc_error:
                print(f"[RAG] Função RPC não disponível, usando busca alternativa: {rpc_error}")
            
            # Fallback: buscar todos os chunks do agente e fazer busca em memória
            result = self.database.supabase.table("agent_knowledge_chunks").select(
                "id, chunk_text, chunk_index, metadata, knowledge_id, embedding"
            ).eq("agent_id", self.agent_id).execute()
            
            if not result.data:
                return []
            
            # Calcular similaridade coseno manualmente
            similarities = []
            for chunk in result.data:
                if chunk.get('embedding'):
                    chunk_emb = chunk['embedding']
                    # Se for lista, converter para numpy array
                    if isinstance(chunk_emb, list):
                        chunk_emb = np.array(chunk_emb)
                    if isinstance(query_embedding, list):
                        query_emb = np.array(query_embedding)
                    else:
                        query_emb = query_embedding
                    
                    # Calcular similaridade coseno
                    dot_product = np.dot(query_emb, chunk_emb)
                    norm_query = np.linalg.norm(query_emb)
                    norm_chunk = np.linalg.norm(chunk_emb)
                    
                    if norm_query > 0 and norm_chunk > 0:
                        similarity = dot_product / (norm_query * norm_chunk)
                        similarities.append((similarity, chunk))
            
            # Ordenar por similaridade e pegar top k
            similarities.sort(key=lambda x: x[0], reverse=True)
            result_chunks = [chunk for _, chunk in similarities[:k]]
            
            # Converter para Document objects
            documents = []
            for chunk in result_chunks:
                # Buscar título do documento original
                title = "Documento"
                if chunk.get('knowledge_id'):
                    try:
                        knowledge_result = self.database.supabase.table("agent_knowledge").select("title").eq("id", chunk['knowledge_id']).execute()
                        if knowledge_result.data:
                            title = knowledge_result.data[0].get('title', 'Documento')
                    except:
                        pass
                
                metadata = chunk.get('metadata', {})
                metadata['title'] = title
                metadata['knowledge_id'] = chunk.get('knowledge_id')
                
                documents.append(Document(
                    page_content=chunk['chunk_text'],
                    metadata=metadata
                ))
            
            return documents
        except Exception as e:
            print(f"[RAG] Erro na busca: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_context(self, query: str, k: int = 3) -> str:
        """Retorna contexto formatado para usar no prompt do agente"""
        docs = self.search(query, k=k)
        if not docs:
            return ""
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            title = doc.metadata.get("title", f"Documento {i}")
            context_parts.append(f"[{title}]\n{doc.page_content}")
        
        return "\n\n".join(context_parts)
    
    def clear_knowledge(self) -> bool:
        """Limpa toda a base de conhecimento do agente"""
        if not self.database:
            return False
        
        try:
            # Buscar todos os knowledge_ids do agente
            result = self.database.supabase.table("agent_knowledge").select("id").eq("agent_id", self.agent_id).execute()
            
            if result.data:
                knowledge_ids = [doc["id"] for doc in result.data]
                
                # Deletar chunks
                for kid in knowledge_ids:
                    self.database.supabase.table("agent_knowledge_chunks").delete().eq("knowledge_id", kid).execute()
                
                # Deletar documentos
                self.database.supabase.table("agent_knowledge").delete().eq("agent_id", self.agent_id).execute()
            
            print(f"[RAG] Base de conhecimento limpa para agente {self.agent_id}")
            return True
        except Exception as e:
            print(f"[RAG] Erro ao limpar: {e}")
            return False
    
    def reload_from_database(self):
        """Recarrega do banco de dados (não precisa mais - já está no Supabase)"""
        # Não precisa fazer nada - os dados já estão no Supabase
        pass
