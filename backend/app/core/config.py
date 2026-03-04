from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# This keeps your DB path consistent across ingestion and the API
CURRENT_DIR = Path(__file__).resolve().parent
APP_DIR = CURRENT_DIR.parent
BACKEND_DIR = APP_DIR.parent

class Settings(BaseSettings):
    
    # Database Config
    CHROMA_PATH: str = str(BACKEND_DIR / "chroma_db")
    KNOWLEDGE_COLLECTION_NAME: str = "sake_knowledge_base"
    SUGGESTION_COLLECTION_NAME: str = "sake_suggestion_base"

    # API Keys (Pydantic will look for these in .env)
    GEMINI_API_KEY: str

    # App Config
    APP_NAME: str = "JunmAI"
    DEBUG_MODE: bool = False

    # Automatically load from .env file
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding='utf-8',
        extra='ignore' # Ignores extra variables in .env
    )

# Create the instance
settings = Settings()

print(BACKEND_DIR)
