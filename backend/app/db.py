import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Find the .env file in the ingestion directory
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(base_dir, "ingestion", ".env")
load_dotenv(env_path)

def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError(f"Missing SUPABASE_URL or SUPABASE_KEY. Checked env path: {env_path}")
    return create_client(url, key)
