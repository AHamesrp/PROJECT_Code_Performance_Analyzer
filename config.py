from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./performance.db")
    
    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    
    # Server
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # API
    API_TITLE: str = "Code Performance Time Machine API"
    API_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
