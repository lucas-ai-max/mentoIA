"""
Script para criar o bucket agent-avatars no Supabase Storage
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase_config import get_supabase_client

# Carregar .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

def create_bucket():
    """Cria o bucket agent-avatars no Supabase Storage"""
    try:
        supabase = get_supabase_client()
        
        print("=" * 60)
        print("Criando bucket 'agent-avatars' no Supabase Storage")
        print("=" * 60)
        print()
        
        # Verificar se o bucket já existe
        try:
            buckets = supabase.storage.list_buckets()
            bucket_names = [b.name for b in buckets]
            
            if "agent-avatars" in bucket_names:
                print("✅ Bucket 'agent-avatars' já existe")
                return True
        except Exception as e:
            print(f"⚠️ Aviso ao verificar buckets: {str(e)}")
        
        # Criar o bucket usando a API
        print("📝 Criando bucket 'agent-avatars'...")
        try:
            # A API do Supabase Python pode não suportar todas as opções
            # Vamos tentar criar de forma simples primeiro
            result = supabase.storage.create_bucket("agent-avatars")
            print("✅ Bucket 'agent-avatars' criado!")
            print("   ⚠️ Configure manualmente no Dashboard:")
            print("      - Marque como 'Public bucket'")
            print("      - Limite de tamanho: 5MB")
            return True
        except Exception as create_error:
            # Se falhar, pode ser que precise ser criado manualmente
            print(f"⚠️ Não foi possível criar via API: {str(create_error)}")
            print()
            print("💡 Crie manualmente no Supabase Dashboard:")
            print("   1. Acesse: https://app.supabase.com")
            print("   2. Vá para Storage")
            print("   3. Clique em 'New bucket'")
            print("   4. Nome: agent-avatars")
            print("   5. Marque como 'Public bucket'")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao criar bucket: {str(e)}")
        print()
        print("💡 Dica: Crie manualmente no Supabase Dashboard:")
        print("   1. Acesse Storage")
        print("   2. Clique em 'New bucket'")
        print("   3. Nome: agent-avatars")
        print("   4. Marque como 'Public bucket'")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_bucket()

