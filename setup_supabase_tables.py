"""
Script para configurar tabelas e buckets no Supabase usando Transaction Pooler
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Carregar .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configurações de conexão
DB_HOST = "aws-1-ca-central-1.pooler.supabase.com"
DB_PORT = 6543
DB_NAME = "postgres"
DB_USER = "postgres.qkdhwwiohaqacojiijya"

# Obter senha do .env ou argumento de linha de comando
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")

# Se não encontrou no .env, tentar argumento de linha de comando
if not DB_PASSWORD and len(sys.argv) > 1:
    DB_PASSWORD = sys.argv[1]

# Se ainda não encontrou, tentar ler do arquivo .env diretamente
if not DB_PASSWORD:
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('SUPABASE_DB_PASSWORD=') and not line.startswith('#'):
                    DB_PASSWORD = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break

# Se ainda não encontrou, pedir ao usuário
if not DB_PASSWORD:
    print("[ERRO] Senha do banco de dados nao encontrada!")
    print()
    print("Opcoes:")
    print("1. Adicione no arquivo .env:")
    print("   SUPABASE_DB_PASSWORD=sua_senha_aqui")
    print()
    print("2. Ou execute com a senha como argumento:")
    print("   python setup_supabase_tables.py sua_senha_aqui")
    print()
    print("3. Ou digite a senha agora (sera usada apenas nesta execucao):")
    try:
        import getpass
        DB_PASSWORD = getpass.getpass("Senha do banco de dados: ")
    except:
        # Fallback se getpass não funcionar
        print("Digite a senha do banco de dados: ", end='', flush=True)
        DB_PASSWORD = input()
    
    if not DB_PASSWORD:
        print("[ERRO] Senha nao fornecida. Abortando.")
        sys.exit(1)

def connect_db():
    """Conecta ao banco de dados usando transaction pooler"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print("[OK] Conectado ao Supabase via Transaction Pooler")
        return conn
    except Exception as e:
        print(f"[ERRO] Erro ao conectar: {str(e)}")
        sys.exit(1)

def check_table_exists(cursor, table_name):
    """Verifica se uma tabela existe"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        );
    """, (table_name,))
    return cursor.fetchone()[0]

def create_agents_table(cursor):
    """Cria a tabela agents se não existir"""
    if check_table_exists(cursor, "agents"):
        print("[OK] Tabela 'agents' ja existe")
        return
    
    print("[INFO] Criando tabela 'agents'...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            avatar TEXT,
            color VARCHAR(7),
            role TEXT NOT NULL,
            goal TEXT NOT NULL,
            backstory TEXT NOT NULL,
            llm_provider VARCHAR(50) NOT NULL,
            llm_model VARCHAR(100) NOT NULL,
            temperature DECIMAL(3,2) DEFAULT 0.7,
            max_tokens INTEGER DEFAULT 1000,
            "verbose" BOOLEAN DEFAULT TRUE,
            allow_delegation BOOLEAN DEFAULT FALSE,
            status VARCHAR(20) DEFAULT 'active',
            tags TEXT[],
            description TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by UUID,
            total_debates INTEGER DEFAULT 0,
            last_used TIMESTAMP WITH TIME ZONE
        );
    """)
    print("[OK] Tabela 'agents' criada")

def update_avatar_column(cursor):
    """Atualiza a coluna avatar para TEXT se necessário"""
    try:
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'agents' 
            AND column_name = 'avatar';
        """)
        result = cursor.fetchone()
        
        if result and result[0] != 'text':
            print("[INFO] Atualizando coluna 'avatar' para TEXT...")
            cursor.execute("""
                ALTER TABLE agents 
                ALTER COLUMN avatar TYPE TEXT;
            """)
            print("[OK] Coluna 'avatar' atualizada para TEXT")
        else:
            print("[OK] Coluna 'avatar' ja e do tipo TEXT")
    except Exception as e:
        print(f"[AVISO] Aviso ao verificar coluna avatar: {str(e)}")

def check_other_tables(cursor):
    """Verifica outras tabelas importantes"""
    tables = ['debates', 'messages', 'folders', 'llm_providers', 'agent_usage_logs']
    
    print("\n[INFO] Status das tabelas:")
    for table in tables:
        exists = check_table_exists(cursor, table)
        status = "[OK] Existe" if exists else "[ERRO] Nao existe"
        print(f"   {table}: {status}")

def check_storage_bucket():
    """Verifica se o bucket de storage existe (via Supabase client)"""
    try:
        from supabase_config import get_supabase_client
        
        supabase = get_supabase_client()
        
        # Tentar listar buckets
        try:
            buckets = supabase.storage.list_buckets()
            bucket_names = [b.name for b in buckets]
            
            if "agent-avatars" in bucket_names:
                print("[OK] Bucket 'agent-avatars' existe no Storage")
                return True
            else:
                print("[ERRO] Bucket 'agent-avatars' NAO existe no Storage")
                print("   Crie manualmente no Supabase Dashboard -> Storage")
                return False
        except Exception as e:
            print(f"[AVISO] Nao foi possivel verificar buckets: {str(e)}")
            print("   Verifique manualmente no Supabase Dashboard")
            return False
    except Exception as e:
        print(f"[AVISO] Erro ao conectar ao Supabase Storage: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Configuração do Supabase - Tabelas e Storage")
    print("=" * 60)
    print()
    
    # Conectar ao banco
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # Criar tabela agents
        create_agents_table(cursor)
        
        # Atualizar coluna avatar
        update_avatar_column(cursor)
        
        # Verificar outras tabelas
        check_other_tables(cursor)
        
        # Verificar storage
        print("\n[INFO] Verificando Storage:")
        check_storage_bucket()
        
        print("\n" + "=" * 60)
        print("[OK] Verificacao concluida!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERRO] Erro durante a execucao: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()
        print("\n[INFO] Conexao fechada")

if __name__ == "__main__":
    main()

