# Configuration Example for AI Personal Finance Advisor
# Copy this file to config.py and fill in your actual API keys

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the AI Personal Finance Advisor"""
    
    # Database Configuration
    POSTGRES_DB = os.getenv("POSTGRES_DB", "financial_advisor_db")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "your_db_user")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "your_secure_password")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Google Gemini Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "your_google_api_key_here")
    GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-pro")
    
    # Financial APIs
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "your_alpha_vantage_api_key_here")
    YAHOO_FINANCE_ENABLED = os.getenv("YAHOO_FINANCE_ENABLED", "true").lower() == "true"
    
    # Firebase Configuration (for mobile apps)
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "your_firebase_project_id")
    FIREBASE_PRIVATE_KEY_ID = os.getenv("FIREBASE_PRIVATE_KEY_ID", "your_firebase_private_key_id")
    FIREBASE_PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY", "your_firebase_private_key")
    FIREBASE_CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL", "your_firebase_client_email")
    FIREBASE_CLIENT_ID = os.getenv("FIREBASE_CLIENT_ID", "your_firebase_client_id")
    
    # AI Model Settings
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your_django_secret_key_here")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key_here")
    
    # Server Configuration
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/financial_advisor.log")

# Example usage:
# config = Config()
# print(f"Database: {config.DATABASE_URL}")
# print(f"OpenAI Model: {config.OPENAI_MODEL}") 