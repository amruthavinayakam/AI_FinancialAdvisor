import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class AIConfig(BaseSettings):
    """Configuration for AI services and APIs"""
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Google Gemini Configuration
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    google_model: str = os.getenv("GOOGLE_MODEL", "gemini-pro")
    
    # Financial APIs
    alpha_vantage_api_key: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    yahoo_finance_enabled: bool = os.getenv("YAHOO_FINANCE_ENABLED", "true").lower() == "true"
    
    # Firebase Configuration
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")
    firebase_private_key_id: str = os.getenv("FIREBASE_PRIVATE_KEY_ID", "")
    firebase_private_key: str = os.getenv("FIREBASE_PRIVATE_KEY", "")
    firebase_client_email: str = os.getenv("FIREBASE_CLIENT_EMAIL", "")
    firebase_client_id: str = os.getenv("FIREBASE_CLIENT_ID", "")
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # AI Model Settings
    max_tokens: int = int(os.getenv("MAX_TOKENS", "4000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    class Config:
        env_file = ".env"
        extra = "ignore"

# Global config instance
ai_config = AIConfig() 