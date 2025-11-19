"""
Configuração do Supabase
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Carregar .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkdhwwiohaqacojiijya.supabase.co")
SUPABASE_SERVICE_ROLE_KEY = os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFrZGh3d2lvaGFxYWNvamlpanlhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzQ5NzgzOCwiZXhwIjoyMDc5MDczODM4fQ.t1ywCrcYDy6J_GWGOQJr4iEtqwfXF-i-7lIOz9wYvPc"
)

def get_supabase_client() -> Client:
    """Retorna cliente Supabase"""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

