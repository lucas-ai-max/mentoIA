"""
Módulo para operações com banco de dados Supabase
"""
from supabase import Client
from typing import List, Dict, Optional
from datetime import datetime
from supabase_config import get_supabase_client

class Database:
    def __init__(self):
        self.supabase: Client = get_supabase_client()
    
    def test_connection(self) -> bool:
        """Testa a conexão com o Supabase"""
        try:
            print("[DB] Testando conexao com Supabase...")
            result = self.supabase.table("debates").select("id").limit(1).execute()
            print("[DB] Conexao com Supabase OK")
            return True
        except Exception as e:
            print(f"[DB] Erro na conexao com Supabase: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def check_tables_exist(self) -> bool:
        """Verifica se as tabelas existem"""
        try:
            print("[DB] Verificando se as tabelas existem...")
            self.supabase.table("debates").select("id").limit(1).execute()
            self.supabase.table("messages").select("id").limit(1).execute()
            print("[DB] Tabelas existem")
            return True
        except Exception as e:
            print(f"[DB] Erro ao verificar tabelas: {str(e)}")
            print("[DB] AVISO: Certifique-se de executar o SQL em supabase_schema.sql no Supabase")
            import traceback
            traceback.print_exc()
            return False
    
    def save_debate(self, pergunta: str, selected_agents: List[str], 
                   num_rodadas: int, historico: List[Dict], sintese: Optional[str] = None) -> str:
        """Salva um debate completo no banco"""
        try:
            print(f"[DB] Tentando salvar debate no banco...")
            print(f"[DB] Pergunta: {pergunta[:50]}...")
            print(f"[DB] Agentes: {selected_agents}")
            print(f"[DB] Historico com {len(historico)} itens")
            
            # Criar debate - garantir que selected_agents seja uma lista válida
            debate_data = {
                "pergunta": pergunta,
                "selected_agents": selected_agents if isinstance(selected_agents, list) else list(selected_agents),
                "num_rodadas": num_rodadas,
                "sintese": sintese
            }
            
            print(f"[DB] Inserindo debate na tabela 'debates'...")
            print(f"[DB] Dados do debate: pergunta={pergunta[:30]}..., agents={len(selected_agents)}, rodadas={num_rodadas}")
            
            debate_result = self.supabase.table("debates").insert(debate_data).execute()
            
            # Verificar se houve erro na resposta
            if hasattr(debate_result, 'error') and debate_result.error:
                raise Exception(f"Erro do Supabase: {debate_result.error}")
            
            if not debate_result.data:
                raise Exception("Nenhum dado retornado ao inserir debate. Verifique se as tabelas existem e RLS está configurado corretamente.")
            
            debate_id = debate_result.data[0]["id"]
            print(f"[DB] Debate criado com ID: {debate_id}")
            
            # Salvar mensagens
            messages_data = []
            for idx, item in enumerate(historico):
                # Limitar tamanho do conteúdo se muito grande
                content = str(item["conteudo"])
                if len(content) > 10000:
                    content = content[:10000] + "... [truncado]"
                
                message = {
                    "debate_id": debate_id,
                    "type": item["tipo"],
                    "content": content,
                    "agent_id": item.get("agente"),
                    "agent_name": item.get("agente"),
                    "agent_role": item.get("agente"),
                    "round_number": item.get("rodada"),
                    "order_index": idx,
                    # Não enviar timestamp - deixar o banco usar DEFAULT
                }
                # Remover campos None para evitar problemas
                message = {k: v for k, v in message.items() if v is not None}
                messages_data.append(message)
            
            if messages_data:
                print(f"[DB] Inserindo {len(messages_data)} mensagens na tabela 'messages'...")
                messages_result = self.supabase.table("messages").insert(messages_data).execute()
                
                # Verificar se houve erro na resposta
                if hasattr(messages_result, 'error') and messages_result.error:
                    raise Exception(f"Erro ao inserir mensagens: {messages_result.error}")
                
                saved_count = len(messages_result.data) if messages_result.data else 0
                print(f"[DB] {saved_count} mensagens salvas")
            else:
                print("[DB] AVISO: Nenhuma mensagem para salvar")
            
            print(f"[DB] Debate salvo no banco: {debate_id}")
            return debate_id
        except Exception as e:
            print(f"[DB] ERRO ao salvar debate: {str(e)}")
            print(f"[DB] Tipo do erro: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_debate(self, debate_id: str) -> Optional[Dict]:
        """Recupera um debate completo"""
        try:
            # Buscar debate
            debate_result = self.supabase.table("debates").select("*").eq("id", debate_id).execute()
            if not debate_result.data:
                return None
            
            debate = debate_result.data[0]
            
            # Buscar mensagens
            messages_result = self.supabase.table("messages")\
                .select("*")\
                .eq("debate_id", debate_id)\
                .order("order_index")\
                .execute()
            
            debate["messages"] = messages_result.data
            return debate
        except Exception as e:
            print(f"[DB] Erro ao buscar debate: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def list_debates(self, limit: int = 50) -> List[Dict]:
        """Lista debates recentes"""
        try:
            result = self.supabase.table("debates")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            return result.data
        except Exception as e:
            print(f"[DB] Erro ao listar debates: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def delete_debate(self, debate_id: str) -> bool:
        """Deleta um debate (cascade deleta mensagens)"""
        try:
            self.supabase.table("debates").delete().eq("id", debate_id).execute()
            print(f"[DB] Debate deletado: {debate_id}")
            return True
        except Exception as e:
            print(f"[DB] Erro ao deletar debate: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def clear_all_data(self) -> bool:
        """Limpa todos os dados do banco (deleta todos os debates e mensagens)"""
        try:
            print("Limpando todos os dados do banco...")
            # Buscar todos os debates primeiro
            debates = self.supabase.table("debates").select("id").execute()
            
            # Deletar mensagens de cada debate
            for debate in debates.data:
                debate_id = debate["id"]
                self.supabase.table("messages").delete().eq("debate_id", debate_id).execute()
            
            # Deletar todos os debates
            self.supabase.table("debates").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            print("Todos os dados foram limpos do banco")
            return True
        except Exception as e:
            print(f"Erro ao limpar banco: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    # ========== MÉTODOS PARA PASTAS ==========
    
    def create_folder(self, name: str, icon: Optional[str] = None, color: Optional[str] = None) -> str:
        """Cria uma nova pasta"""
        try:
            folder_data = {
                "name": name,
                "icon": icon,
                "color": color
            }
            result = self.supabase.table("folders").insert(folder_data).execute()
            if not result.data:
                raise Exception("Nenhum dado retornado ao criar pasta")
            folder_id = result.data[0]["id"]
            print(f"[DB] Pasta criada: {folder_id} - {name}")
            return folder_id
        except Exception as e:
            print(f"[DB] Erro ao criar pasta: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def list_folders(self) -> List[Dict]:
        """Lista todas as pastas com contagem de debates"""
        try:
            folders_result = self.supabase.table("folders")\
                .select("*")\
                .order("created_at", desc=False)\
                .execute()
            
            folders = folders_result.data if folders_result.data else []
            
            # Adicionar contagem de debates para cada pasta
            for folder in folders:
                count_result = self.supabase.table("debates")\
                    .select("id", count="exact")\
                    .eq("folder_id", folder["id"])\
                    .execute()
                folder["count"] = count_result.count if hasattr(count_result, 'count') else 0
            
            return folders
        except Exception as e:
            print(f"[DB] Erro ao listar pastas: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def update_folder(self, folder_id: str, name: Optional[str] = None, 
                     icon: Optional[str] = None, color: Optional[str] = None) -> bool:
        """Atualiza uma pasta"""
        try:
            update_data = {}
            if name is not None:
                update_data["name"] = name
            if icon is not None:
                update_data["icon"] = icon
            if color is not None:
                update_data["color"] = color
            
            if not update_data:
                return True
            
            update_data["updated_at"] = datetime.now().isoformat()
            
            self.supabase.table("folders")\
                .update(update_data)\
                .eq("id", folder_id)\
                .execute()
            
            print(f"[DB] Pasta atualizada: {folder_id}")
            return True
        except Exception as e:
            print(f"[DB] Erro ao atualizar pasta: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def delete_folder(self, folder_id: str) -> bool:
        """Deleta uma pasta (os debates ficam sem pasta)"""
        try:
            # Primeiro, remover folder_id dos debates
            self.supabase.table("debates")\
                .update({"folder_id": None})\
                .eq("folder_id", folder_id)\
                .execute()
            
            # Depois deletar a pasta
            self.supabase.table("folders").delete().eq("id", folder_id).execute()
            print(f"[DB] Pasta deletada: {folder_id}")
            return True
        except Exception as e:
            print(f"[DB] Erro ao deletar pasta: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def move_debate_to_folder(self, debate_id: str, folder_id: Optional[str]) -> bool:
        """Move um debate para uma pasta (folder_id=None remove da pasta)"""
        try:
            update_data = {"folder_id": folder_id}
            self.supabase.table("debates")\
                .update(update_data)\
                .eq("id", debate_id)\
                .execute()
            print(f"[DB] Debate {debate_id} movido para pasta {folder_id}")
            return True
        except Exception as e:
            print(f"[DB] Erro ao mover debate: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

