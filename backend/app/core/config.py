from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# This keeps your DB path consistent across ingestion and the API
CURRENT_DIR = Path(__file__).resolve().parent
APP_DIR = CURRENT_DIR.parent
BACKEND_DIR = APP_DIR.parent

class Settings(BaseSettings):
    
    CHROMA_PATH: str = str(BACKEND_DIR / "chroma_db")
    KNOWLEDGE_COLLECTION_NAME: str = "sake_knowledge_base"

    # We'll leave placeholders for your future secrets
    # OPENAI_API_KEY: str = "" 

# Create the instance
settings = Settings()

print(BACKEND_DIR)
